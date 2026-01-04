import React, { useState, useEffect } from 'react';
import { StockTicker, WatchlistItem, Notification } from './types';
import { scanMarket } from './services/marketService';
import { CandlestickChart } from './components/CandlestickChart';
import { StockCard } from './components/StockCard';
import { RiskCalculator } from './components/RiskCalculator';
import { Search, Sliders, Activity, BarChart2, DollarSign, PlayCircle, RefreshCw, AlertCircle, Target, TrendingUp, TrendingDown, Star, Bell, X, Menu, Zap } from 'lucide-react';

const App: React.FC = () => {
  const [stocks, setStocks] = useState<StockTicker[]>([]);
  const [selectedStock, setSelectedStock] = useState<StockTicker | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [hasScanned, setHasScanned] = useState(false);
  
  // Strategy State
  const [strategy, setStrategy] = useState<'standard' | 'power_play'>('standard');

  // Watchlist & Notifications
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showWatchlistOnly, setShowWatchlistOnly] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Filter stocks based on view mode
  const displayStocks = showWatchlistOnly 
    ? stocks.filter(s => watchlist.some(w => w.symbol === s.symbol))
    : stocks;

  const handleScan = async () => {
    setIsScanning(true);
    setHasScanned(false);
    setSelectedStock(null);
    setShowWatchlistOnly(false);
    
    // Simulate API call to Python backend with strategy param
    const results = await scanMarket(strategy);
    
    setStocks(results);
    if (results.length > 0) {
      setSelectedStock(results[0]);
    }
    setIsScanning(false);
    setHasScanned(true);
  };

  const toggleWatchlist = (stock: StockTicker) => {
    const exists = watchlist.find(w => w.symbol === stock.symbol);
    if (exists) {
      setWatchlist(watchlist.filter(w => w.symbol !== stock.symbol));
    } else {
      setWatchlist([...watchlist, { symbol: stock.symbol, alertPrice: stock.vcp.stopLoss }]);
      
      // Simulate a notification trigger immediately for demo purposes if price is near stop
      if (stock.price <= stock.vcp.stopLoss * 1.05) {
             }
    }
  };

  const addNotification = (title: string, message: string) => {
    const newNotif: Notification = {
      id: Date.now().toString(),
      title,
      message,
      timestamp: new Date()
    };
    setNotifications(prev => [newNotif, ...prev]);
    // Auto remove after 5 seconds
    setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== newNotif.id));
    }, 5000);
  };

  const isInWatchlist = (symbol: string) => watchlist.some(w => w.symbol === symbol);

  return (
    <div className="min-h-screen bg-darkBg text-slate-100 flex flex-col md:flex-row font-sans selection:bg-blue-500 selection:text-white">
      
      {/* Notifications Toast Container */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        {notifications.map(n => (
          <div key={n.id} className="bg-slate-800 border-l-4 border-blue-500 text-white p-4 rounded shadow-2xl pointer-events-auto animate-bounce-in max-w-sm">
             <div className="flex justify-between items-start">
               <h4 className="font-bold text-sm flex items-center gap-2"><Bell size={14} className="text-blue-400"/> {n.title}</h4>
               <button onClick={() => setNotifications(prev => prev.filter(x => x.id !== n.id))}><X size={14} className="text-slate-400 hover:text-white"/></button>
             </div>
             <p className="text-xs text-slate-300 mt-1">{n.message}</p>
             <div className="text-[10px] text-slate-500 mt-2 text-right">{n.timestamp.toLocaleTimeString()}</div>
          </div>
        ))}
      </div>

      {/* Mobile Header */}
      <div className="md:hidden bg-slate-900 border-b border-slate-800 p-4 flex justify-between items-center sticky top-0 z-20">
        <h1 className="text-lg font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 flex items-center gap-2">
            <Activity className="text-blue-500" size={20} />
            VCP Hunter
        </h1>
        <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-slate-400">
           {mobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Sidebar / Navigation */}
      <aside className={`
        w-full md:w-80 bg-slate-900 border-r border-slate-800 flex flex-col 
        fixed md:sticky top-0 z-10 h-screen transition-transform duration-300
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        md:h-screen
      `}>
        <div className="hidden md:block p-6 border-b border-slate-800">
          <h1 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 flex items-center gap-2">
            <Activity className="text-blue-500" />
            VCP Hunter
          </h1>
          <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider font-semibold">Kristjan-TW Strategy</p>
        </div>

        <div className="p-4 space-y-6 flex-1 overflow-y-auto custom-scrollbar pb-20 md:pb-4">
          
          {/* Strategy Selector */}
          <div className="bg-slate-800 p-1 rounded-lg flex shadow-inner">
             <button 
                onClick={() => setStrategy('standard')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex items-center justify-center gap-2 ${strategy === 'standard' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
             >
                <Activity size={14} /> 標準 VCP
             </button>
             <button 
                onClick={() => setStrategy('power_play')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex items-center justify-center gap-2 ${strategy === 'power_play' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
             >
                <Zap size={14} /> 強力動能
             </button>
          </div>

          {/* Controls */}
          <div className="space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 text-slate-500 w-4 h-4" />
              <input 
                type="text" 
                placeholder="輸入代號 (e.g. 2330)" 
                className="w-full bg-slate-800 border border-slate-700 rounded-lg py-2 pl-9 pr-4 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
              />
            </div>
            
            <div className="flex gap-2">
              <button 
                onClick={handleScan}
                disabled={isScanning}
                className={`
                  flex-1 py-3 px-4 rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg transition-all text-sm
                  ${isScanning 
                    ? 'bg-slate-700 text-slate-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-500 text-white hover:scale-[1.02] shadow-blue-900/20'}
                `}
              >
                {isScanning ? <RefreshCw className="animate-spin w-4 h-4" /> : <PlayCircle className="w-4 h-4" />}
                {isScanning ? '掃描中' : '全市場掃描'}
              </button>

              <button 
                 onClick={() => { setShowWatchlistOnly(!showWatchlistOnly); setMobileMenuOpen(false); }}
                 className={`px-3 rounded-lg border flex items-center justify-center transition-all ${showWatchlistOnly ? 'bg-yellow-500/20 border-yellow-500 text-yellow-400' : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'}`}
              >
                 <Star size={18} fill={showWatchlistOnly ? "currentColor" : "none"} />
              </button>
            </div>
          </div>

          {/* Filter Config (Visual Only) */}
          <div className="space-y-3">
             <div className="flex items-center gap-2 text-slate-400 text-sm uppercase tracking-wider font-semibold mb-2">
               <Sliders className="w-4 h-4" /> 策略參數: {strategy === 'standard' ? '標準' : '動能'}
             </div>
             <div className="bg-slate-800/50 p-3 rounded border border-slate-700/50 text-xs space-y-2">
               {strategy === 'standard' ? (
                 <>
                   <div className="flex justify-between">
                     <span className="text-slate-400">趨勢過濾</span><span className="text-green-400 font-mono">Stage 2</span>
                   </div>
                   <div className="flex justify-between">
                     <span className="text-slate-400">均線條件</span><span className="text-blue-300 font-mono">P &gt; 50 &gt; 200</span>
                   </div>
                   <div className="flex justify-between">
                     <span className="text-slate-400">籌碼面</span><span className="text-purple-300 font-mono">法人連買</span>
                   </div>
                 </>
               ) : (
                 <>
                   <div className="flex justify-between">
                     <span className="text-slate-400">趨勢強度</span><span className="text-purple-400 font-mono">&gt; 10MA &gt; 20MA</span>
                   </div>
                   <div className="flex justify-between">
                     <span className="text-slate-400">動能指標</span><span className="text-blue-300 font-mono">+20% / 40天</span>
                   </div>
                   <div className="flex justify-between">
                     <span className="text-slate-400">緊湊度</span><span className="text-yellow-300 font-mono">高點 10% 內</span>
                   </div>
                 </>
               )}
             </div>
          </div>

          {/* Results List (In Sidebar on Desktop) */}
          <div className="md:block">
            <div className="flex justify-between items-center mb-2 mt-4 md:mt-0">
              <h2 className="text-sm font-bold text-slate-300">{showWatchlistOnly ? '追蹤清單' : '掃描結果'}</h2>
              <span className="bg-slate-800 text-slate-400 text-[10px] px-2 py-0.5 rounded-full font-mono">{displayStocks.length}</span>
            </div>
            
            <div className="space-y-3">
              {displayStocks.map(stock => (
                 <div key={stock.symbol} className="relative group">
                    <StockCard 
                      stock={stock} 
                      isSelected={selectedStock?.symbol === stock.symbol}
                      onSelect={(s) => { setSelectedStock(s); setMobileMenuOpen(false); }}
                    />
                    {/* Quick Watch Toggle */}
                    <button 
                      onClick={(e) => { e.stopPropagation(); toggleWatchlist(stock); }}
                      className="absolute top-2 right-2 p-1.5 rounded-full bg-slate-900/80 text-slate-400 hover:text-yellow-400 transition-colors z-10"
                    >
                      <Star size={14} fill={isInWatchlist(stock.symbol) ? "#facc15" : "none"} className={isInWatchlist(stock.symbol) ? "text-yellow-400" : ""} />
                    </button>
                 </div>
              ))}
              {displayStocks.length === 0 && hasScanned && (
                <div className="p-8 text-center border border-dashed border-slate-700 rounded-xl text-slate-500 text-sm">
                  <AlertCircle className="mx-auto mb-2 w-6 h-6" />
                  <p>{showWatchlistOnly ? '暫無追蹤標的' : '未發現符合標的'}</p>
                </div>
              )}
            </div>
          </div>

          <div className="md:mt-auto pt-6 text-[10px] text-slate-600">
             <p>系統版本 v1.3.0 (Power Play)</p>
             <p>資料來源: FinMind Open Data</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-8 overflow-y-auto h-[calc(100vh-60px)] md:h-screen bg-darkBg">
        {!hasScanned && !isScanning && !selectedStock && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4 opacity-50">
             <Activity size={64} strokeWidth={1} />
             <p className="text-lg">點擊「開始全市場掃描」</p>
          </div>
        )}

        {isScanning && !hasScanned && (
           <div className="h-full flex flex-col items-center justify-center text-blue-400 space-y-4">
             <RefreshCw size={48} className="animate-spin" />
             <p className="text-lg animate-pulse text-center">正在連線 FinMind API<br/><span className="text-sm text-slate-500">分析技術指標與籌碼...</span></p>
           </div>
        )}

        {selectedStock && (
            <div className="space-y-6 max-w-5xl mx-auto pb-10">
              
              {/* Header Card */}
              <div className="bg-slate-800 rounded-xl p-4 md:p-6 border border-slate-700 shadow-xl relative">
                
                {/* Watchlist Toggle (Main) */}
                <button 
                   onClick={() => toggleWatchlist(selectedStock)}
                   className="absolute top-4 right-4 p-2 rounded-full bg-slate-700/50 hover:bg-slate-700 transition-colors"
                >
                   <Star 
                     size={24} 
                     fill={isInWatchlist(selectedStock.symbol) ? "#facc15" : "none"} 
                     className={isInWatchlist(selectedStock.symbol) ? "text-yellow-400" : "text-slate-400"} 
                   />
                </button>

                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    <div className="flex items-center gap-4">
                      <div>
                        <h1 className="text-2xl md:text-3xl font-bold text-white flex flex-wrap items-center gap-2">
                          {selectedStock.name} 
                          <span className="text-lg md:text-xl text-slate-400 font-mono">{selectedStock.symbol}</span>
                        </h1>
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-xs md:text-sm text-slate-400 flex items-center gap-1 bg-slate-900/50 px-2 py-0.5 rounded">
                            <BarChart2 size={12} /> {selectedStock.sector}
                          </span>
                          {/* Strategy Badge */}
                          <span className={`text-xs md:text-sm flex items-center gap-1 px-2 py-0.5 rounded ${strategy === 'power_play' ? 'bg-purple-900/50 text-purple-400' : 'bg-blue-900/50 text-blue-400'}`}>
                            {strategy === 'power_play' ? <Zap size={12} /> : <Activity size={12} />}
                            {strategy === 'power_play' ? 'Power Play' : 'Standard VCP'}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex flex-row items-center gap-6 w-full md:w-auto">
                      <div className="flex flex-col">
                        <div className={`text-4xl font-mono font-bold tracking-tight ${selectedStock.changePct >= 0 ? 'text-twRed' : 'text-twGreen'}`}>
                          {selectedStock.price}
                        </div>
                        <div className={`flex items-center gap-1 text-sm font-bold ${selectedStock.changePct >= 0 ? 'text-twRed' : 'text-twGreen'}`}>
                          {selectedStock.changePct >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                          {selectedStock.changePct > 0 ? '+' : ''}{selectedStock.changePct}%
                        </div>
                      </div>

                      <div className="h-10 w-px bg-slate-700 mx-2"></div>

                      <div className="flex flex-col text-right flex-1 md:flex-none">
                         <span className="text-xs text-slate-400">成交量</span>
                         <span className="font-mono font-bold text-slate-200">{selectedStock.candles[selectedStock.candles.length-1].volume.toLocaleString()} 張</span>
                      </div>
                    </div>
                </div>

                {/* Quick Chips & Fundamentals Row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t border-slate-700">
                    <div className="bg-slate-900/50 p-2 rounded text-center">
                        <div className="text-[10px] text-slate-400">外資 (5日)</div>
                        <div className={`font-mono font-bold ${selectedStock.chips.foreignNetBuy > 0 ? 'text-purple-400' : 'text-slate-400'}`}>
                            {selectedStock.chips.foreignNetBuy > 0 ? '+' : ''}{selectedStock.chips.foreignNetBuy}
                        </div>
                    </div>
                    <div className="bg-slate-900/50 p-2 rounded text-center">
                        <div className="text-[10px] text-slate-400">投信 (5日)</div>
                        <div className={`font-mono font-bold ${selectedStock.chips.trustNetBuy > 0 ? 'text-purple-400' : 'text-slate-400'}`}>
                             {selectedStock.chips.trustNetBuy > 0 ? '+' : ''}{selectedStock.chips.trustNetBuy}
                        </div>
                    </div>
                    <div className="bg-slate-900/50 p-2 rounded text-center">
                        <div className="text-[10px] text-slate-400">月營收 YoY</div>
                        <div className="text-yellow-400 font-mono font-bold">{selectedStock.fundamentals.revenueYoy}%</div>
                    </div>
                    <div className="bg-slate-900/50 p-2 rounded text-center">
                        <div className="text-[10px] text-slate-400">收縮型態</div>
                        <div className="text-blue-400 font-mono font-bold">{selectedStock.vcp.contractions}T</div>
                    </div>
                </div>
              </div>

              {/* Chart Section */}
              <div className="bg-slate-800 rounded-xl p-1 border border-slate-700 shadow-xl overflow-hidden">
                  <div className="p-3 border-b border-slate-700 bg-slate-800 flex justify-between items-center">
                    <h3 className="font-bold text-slate-300 text-sm md:text-base">K線圖 (日)</h3>
                    <div className="flex gap-3 text-[10px]">
                        <span className="text-yellow-400">● 10MA</span>
                        <span className="text-purple-400">● 20MA</span>
                        <span className="text-cyan-400">● 50MA</span>
                    </div>
                  </div>
                  <CandlestickChart 
                    data={selectedStock.candles} 
                    pivotPrice={selectedStock.vcp.pivotPrice} 
                    stopLoss={selectedStock.vcp.stopLoss}
                  />
              </div>

              {/* Risk Management Module (New) */}
              <RiskCalculator 
                 currentPrice={selectedStock.price} 
                 suggestedStopLoss={selectedStock.vcp.stopLoss}
                 symbol={selectedStock.symbol}
              />

              {/* Strategy Plan */}
              <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-5 border border-slate-700 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-24 h-24 bg-blue-600/10 rounded-full blur-3xl"></div>
                  <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                    <Target className="text-blue-500" size={18} /> 交易策略詳情
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-slate-900/80 p-4 rounded-lg border border-slate-700 flex flex-col">
                        <span className="text-slate-500 text-xs uppercase mb-1">進場 (Pivot Breakout)</span>
                        <span className="text-2xl font-mono font-bold text-blue-400">{selectedStock.vcp.pivotPrice}</span>
                        <span className="text-[10px] text-slate-500 mt-1">突破此價位且量增</span>
                    </div>
                    <div className="bg-slate-900/80 p-4 rounded-lg border border-slate-700 flex flex-col">
                        <span className="text-slate-500 text-xs uppercase mb-1">止損 (Dynamic SL)</span>
                        <span className="text-2xl font-mono font-bold text-twGreen">{selectedStock.vcp.stopLoss}</span>
                        <span className="text-[10px] text-slate-500 mt-1">
                          {strategy === 'power_play' ? '前波低點保護 (緊縮)' : '前波低點保護 (波段)'}
                        </span>
                    </div>
                    <div className="bg-slate-900/80 p-4 rounded-lg border border-slate-700 flex flex-col">
                        <span className="text-slate-500 text-xs uppercase mb-1">目標 (Risk:Reward 1:3)</span>
                        <span className="text-2xl font-mono font-bold text-twRed">{selectedStock.vcp.target1}</span>
                        <span className="text-[10px] text-slate-500 mt-1">第一階段獲利點</span>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-slate-700/50">
                      <p className="text-sm text-slate-300 leading-relaxed">
                        <span className="text-blue-500 font-bold">AI 分析摘要:</span> {selectedStock.reason}
                      </p>
                  </div>
              </div>

            </div>
        )}
      </main>
    </div>
  );
};

export default App;
