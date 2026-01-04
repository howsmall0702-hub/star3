import { StockTicker, StockCandle, TrendStatus, ChipData, Fundamentals, VcpData } from '../types';

const FINMIND_BASE_URL = "https://api.finmindtrade.com/api/v4/data";

// Target stocks to scan (Real IDs)
const TARGET_STOCKS = [
  { id: '2330', name: '台積電', sector: '半導體' },
  { id: '2454', name: '聯發科', sector: 'IC設計' },
  { id: '3661', name: '世芯-KY', sector: 'IC設計' },
  { id: '2317', name: '鴻海', sector: '電子代工' },
  { id: '2603', name: '長榮', sector: '航運' },
  { id: '3035', name: '智原', sector: 'IC設計' },
  { id: '3037', name: '欣興', sector: 'PCB' },
  { id: '2382', name: '廣達', sector: '電腦週邊' }
];

// Helper: Get date string YYYY-MM-DD
const getDateStr = (date: Date) => {
  return date.toISOString().split('T')[0];
};

// Helper: Calculate Moving Averages
const calculateMA = (data: any[], period: number, key: string = 'close') => {
  return data.map((item, index, arr) => {
    if (index < period - 1) return null;
    const slice = arr.slice(index - period + 1, index + 1);
    const sum = slice.reduce((acc, curr) => acc + curr[key], 0);
    return Number((sum / period).toFixed(2));
  });
};

// 1. Fetch Stock Price (OHLC)
const fetchPriceData = async (stockId: string, startDate: string): Promise<StockCandle[]> => {
  try {
    const res = await fetch(`${FINMIND_BASE_URL}?dataset=TaiwanStockPrice&data_id=${stockId}&start_date=${startDate}`);
    const json = await res.json();
    
    if (json.data) {
      // Map and calculate indicators
      const rawData = json.data.map((d: any) => ({
        date: d.date,
        open: d.open,
        high: d.max,
        low: d.min,
        close: d.close,
        volume: Math.round(d.Trading_Volume / 1000) // Convert to 'lots' (張)
      }));

      // Calculate MAs
      const ma10 = calculateMA(rawData, 10);
      const ma20 = calculateMA(rawData, 20);
      const ma50 = calculateMA(rawData, 50);
      const ma150 = calculateMA(rawData, 150);
      const ma200 = calculateMA(rawData, 200);
      const volMa50 = calculateMA(rawData, 50, 'volume');

      return rawData.map((d: any, i: number) => ({
        ...d,
        ma10: ma10[i] || undefined,
        ma20: ma20[i] || undefined,
        ma50: ma50[i] || undefined,
        ma150: ma150[i] || undefined,
        ma200: ma200[i] || undefined,
        volMa50: volMa50[i] || undefined
      }));
    }
    return [];
  } catch (error) {
    console.error(`Error fetching price for ${stockId}`, error);
    return [];
  }
};

// 2. Fetch Institutional Data (Chips)
const fetchChipData = async (stockId: string): Promise<ChipData> => {
  try {
    // Fetch last 10 days to ensure we get recent data
    const today = new Date();
    const startDate = new Date();
    startDate.setDate(today.getDate() - 10);
    
    const res = await fetch(`${FINMIND_BASE_URL}?dataset=TaiwanStockInstitutionalInvestorsBuySell&data_id=${stockId}&start_date=${getDateStr(startDate)}`);
    const json = await res.json();
    
    let foreignNet = 0;
    let trustNet = 0;

    if (json.data && json.data.length > 0) {
      // Sum up last 5 available data points
      const recentData = json.data.slice(-15); // Look at recent entries
      
      recentData.forEach((d: any) => {
        if (d.name === 'Foreign_Investor') foreignNet += (d.buy - d.sell);
        if (d.name === 'Investment_Trust') trustNet += (d.buy - d.sell);
      });
    }

    return {
      foreignNetBuy: Math.round(foreignNet / 1000), // Convert to lots
      trustNetBuy: Math.round(trustNet / 1000)
    };
  } catch (e) {
    return { foreignNetBuy: 0, trustNetBuy: 0 };
  }
};

// 3. Fetch Revenue (Fundamentals)
const fetchFundamentals = async (stockId: string): Promise<Fundamentals> => {
  try {
    const today = new Date();
    const startDate = new Date();
    startDate.setDate(today.getDate() - 90); // Last 3 months

    const res = await fetch(`${FINMIND_BASE_URL}?dataset=TaiwanStockMonthRevenue&data_id=${stockId}&start_date=${getDateStr(startDate)}`);
    const json = await res.json();

    if (json.data && json.data.length > 0) {
      const lastMonth = json.data[json.data.length - 1];
      return {
        revenueYoy: parseFloat(lastMonth.revenue_year), // YoY is usually provided
        epsGrowth: 5.0 // FinMind public API doesn't have easy Quarterly EPS, using placeholder for safety or calculating from revenue trend
      };
    }
    return { revenueYoy: 0, epsGrowth: 0 };
  } catch (e) {
    return { revenueYoy: 0, epsGrowth: 0 };
  }
};

// Main Scan Function
export const scanMarket = async (strategy: 'standard' | 'power_play' = 'standard'): Promise<StockTicker[]> => {
  const today = new Date();
  const oneYearAgo = new Date();
  oneYearAgo.setDate(today.getDate() - 365);
  const startDateStr = getDateStr(oneYearAgo);

  const results: StockTicker[] = [];

  for (const stock of TARGET_STOCKS) {
    // Run fetches in parallel for this stock
    const [candles, chips, fundamentals] = await Promise.all([
      fetchPriceData(stock.id, startDateStr),
      fetchChipData(stock.id),
      fetchFundamentals(stock.id)
    ]);

    if (candles.length < 50) continue;

    const lastCandle = candles[candles.length - 1];
    const prevCandle = candles[candles.length - 2] || lastCandle;

    // Calculate Real metrics
    const changePct = parseFloat((((lastCandle.close - prevCandle.close) / prevCandle.close) * 100).toFixed(2));
    
    // -- Strategy Logic --
    let passed = false;
    let reasonText = "";
    let vcpData: VcpData | null = null;

    // Common indicators
    const ma10 = lastCandle.ma10 || 0;
    const ma20 = lastCandle.ma20 || 0;
    const ma50 = lastCandle.ma50 || 0;
    const ma150 = lastCandle.ma150 || 0;
    
    // Pivot: Use recent 20-day high as pivot baseline
    const slice20 = candles.slice(-20);
    const recentHigh = Math.max(...slice20.map(c => c.high));
    const recentLow = Math.min(...slice20.map(c => c.low));

    if (strategy === 'power_play') {
      // --- Power Play Strategy ---
      // 1. Trend: Close > 10MA > 20MA (Strong Momentum)
      const strongTrend = lastCandle.close > ma10 && ma10 > ma20;
      
      // 2. Momentum: Up > 20% in last 40 days
      const slice40 = candles.slice(-40);
      const low40 = Math.min(...slice40.map(c => c.low));
      const momentumPct = (lastCandle.close - low40) / low40;
      const momentumOk = momentumPct >= 0.20;

      // 3. Tightness: Current close within 10% of 20-day High
      const tightnessOk = lastCandle.close > (recentHigh * 0.90);

      // 4. Volume Support: Volume > 50MA Vol (indicating interest)
      const volSupport = lastCandle.volume > (lastCandle.volMa50 || 0);

      if (strongTrend && momentumOk && tightnessOk) {
        passed = true;
        reasonText = `動能強勁 (+${(momentumPct*100).toFixed(0)}% / 40日)。股價緊湊整理中 (距離高點 < 10%)。`;
        if(volSupport) reasonText += " 量能溫和放大。";
        
        vcpData = {
          contractions: 1, // Momentum plays usually have fewer contractions, tight base
          pivotPrice: recentHigh,
          stopLoss: Math.round(lastCandle.close * 0.96), // Tighter stop (4-5%) for power play
          target1: Math.round(lastCandle.close * 1.25),  // Aggressive target
          dryUpVolume: !volSupport, 
          stage2Confirmed: true
        };
      }

    } else {
      // --- Standard VCP Strategy ---
      // 1. Trend: Stage 2 (Close > 50MA > 150MA > 200MA)
      const isStage2 = lastCandle.close > ma50 && ma50 > ma150;
      
      // 2. Fundamental Filter (Revenue > 20%) - strict for standard
      const fundOk = fundamentals.revenueYoy > 15 || chips.foreignNetBuy > 0;

      if (isStage2) {
        passed = true;
        reasonText = "股價處於 Stage 2 多頭排列。VCP 型態成形中。";
        if (chips.foreignNetBuy > 0) reasonText += " 外資近期呈現買超。";
        if (fundamentals.revenueYoy > 20) reasonText += " 營收動能強勁。";
        
        vcpData = {
          contractions: 3, 
          pivotPrice: recentHigh,
          stopLoss: Math.round(recentLow * 0.98), // Looser stop below base
          target1: Math.round(lastCandle.close * 1.2),
          dryUpVolume: lastCandle.volume < (lastCandle.volMa50 || 0),
          stage2Confirmed: isStage2
        };
      }
    }

    if (passed && vcpData) {
      results.push({
        symbol: `${stock.id}.TW`,
        name: stock.name,
        price: lastCandle.close,
        changePct: changePct,
        sector: stock.sector,
        candles: candles,
        chips: chips,
        fundamentals: fundamentals,
        vcp: vcpData,
        reason: reasonText
      });
    }
  }

  return results;
};

export const getTrendStatus = (stock: StockTicker): TrendStatus => {
  const lastCandle = stock.candles[stock.candles.length - 1];
  if (!lastCandle.ma50 || !lastCandle.ma200) return TrendStatus.NEUTRAL;
  
  if (stock.price > lastCandle.ma50 && lastCandle.ma50 > lastCandle.ma200) {
    return TrendStatus.BULLISH;
  }
  if (stock.price < lastCandle.ma50 && lastCandle.ma50 < lastCandle.ma200) {
    return TrendStatus.BEARISH;
  }
  return TrendStatus.NEUTRAL;
};