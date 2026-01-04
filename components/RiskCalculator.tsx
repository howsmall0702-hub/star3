import React, { useState, useEffect } from 'react';
import { Calculator, AlertTriangle, ShieldCheck, DollarSign } from 'lucide-react';

interface Props {
  currentPrice: number;
  suggestedStopLoss: number;
  symbol: string;
}

export const RiskCalculator: React.FC<Props> = ({ currentPrice, suggestedStopLoss, symbol }) => {
  // Default states
  const [capital, setCapital] = useState<number>(1000000); // Default 1M TWD
  const [riskPct, setRiskPct] = useState<number>(1.0); // Default 1%
  const [customStopLoss, setCustomStopLoss] = useState<number>(suggestedStopLoss);

  // Calculated values
  const [positionSize, setPositionSize] = useState<number>(0);
  const [unit, setUnit] = useState<string>('張'); // '張' or '股'
  const [riskAmount, setRiskAmount] = useState<number>(0);
  const [totalCost, setTotalCost] = useState<number>(0);

  useEffect(() => {
    // 1. Calculate Max Risk allowed
    const maxRiskAmount = capital * (riskPct / 100);
    
    // 2. Calculate Risk per Share
    // If Stop Loss > Price (Short), logic reverses, but assuming Long strategy here.
    const riskPerShare = currentPrice - customStopLoss;

    if (riskPerShare <= 0) {
      setPositionSize(0);
      setRiskAmount(0);
      setTotalCost(0);
      setUnit('張');
      return;
    }

    // 3. Calculate max shares
    const maxSharesByRisk = maxRiskAmount / riskPerShare;
    
    // 4. Calculate max shares by capital (no margin)
    const maxSharesByCapital = capital / currentPrice;

    // 5. Take the smaller of the two (Risk constraint vs Capital constraint)
    const finalShares = Math.min(maxSharesByRisk, maxSharesByCapital);

    // 6. Logic: If shares < 1000, show shares (Odd Lot). Else show Lots.
    let displayQty = 0;
    let displayUnit = '張';
    let actualSharesCalc = 0;

    if (finalShares >= 1000) {
        displayQty = Math.floor(finalShares / 1000);
        displayUnit = '張';
        actualSharesCalc = displayQty * 1000;
    } else {
        displayQty = Math.floor(finalShares);
        displayUnit = '股';
        actualSharesCalc = displayQty;
    }

    setPositionSize(displayQty);
    setUnit(displayUnit);
    setRiskAmount(Math.round(actualSharesCalc * riskPerShare));
    setTotalCost(Math.round(actualSharesCalc * currentPrice));

  }, [capital, riskPct, customStopLoss, currentPrice]);

  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-lg">
      <div className="flex items-center gap-2 mb-4 border-b border-slate-700 pb-3">
        <ShieldCheck className="text-emerald-400" size={20} />
        <h3 className="font-bold text-white">部位風險控管模組</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Inputs */}
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-slate-400 mb-1 uppercase font-bold tracking-wider">總資金 (TWD)</label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-2.5 text-slate-500 w-4 h-4" />
              <input 
                type="number" 
                value={capital}
                onChange={(e) => setCapital(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 pl-9 pr-3 text-white focus:ring-2 focus:ring-blue-500 outline-none font-mono"
              />
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1 uppercase font-bold tracking-wider">單筆風險 (%)</label>
              <input 
                type="number" 
                step="0.1"
                value={riskPct}
                onChange={(e) => setRiskPct(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none font-mono text-center"
              />
            </div>
            <div className="flex-1">
              <label className="block text-xs text-slate-400 mb-1 uppercase font-bold tracking-wider">止損價 (SL)</label>
              <input 
                type="number" 
                step="0.1"
                value={customStopLoss}
                onChange={(e) => setCustomStopLoss(Number(e.target.value))}
                className={`w-full bg-slate-900 border rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none font-mono text-center ${customStopLoss >= currentPrice ? 'border-red-500 text-red-400' : 'border-slate-700'}`}
              />
            </div>
          </div>
        </div>

        {/* Right: Results */}
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 flex flex-col justify-center">
            <div className="flex justify-between items-center mb-2">
                <span className="text-slate-400 text-sm">建議買進{unit === '張' ? '張數' : '股數'}</span>
                <span className="text-3xl font-mono font-bold text-blue-400">{positionSize} <span className="text-sm text-slate-500">{unit}</span></span>
            </div>
            
            <div className="space-y-2 mt-2 pt-2 border-t border-slate-800">
                <div className="flex justify-between text-sm">
                    <span className="text-slate-500">預期最大虧損</span>
                    <span className="text-red-400 font-mono font-bold">-{riskAmount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-slate-500">部位總市值</span>
                    <span className="text-slate-300 font-mono">{totalCost.toLocaleString()}</span>
                </div>
                {totalCost >= capital && (
                   <div className="flex items-center gap-1 text-[10px] text-yellow-500 mt-1">
                      <AlertTriangle size={12} /> 受限於總資金上限
                   </div>
                )}
            </div>
        </div>
      </div>
      
      <div className="mt-4 text-[10px] text-slate-500 text-center">
         *此計算不包含交易手續費與稅金，僅供風險評估參考。
      </div>
    </div>
  );
};