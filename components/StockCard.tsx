import React from 'react';
import { StockTicker, TrendStatus } from '../types';
import { TrendingUp, AlertTriangle, Target, DollarSign, Activity } from 'lucide-react';
import { getTrendStatus } from '../services/marketService';

interface Props {
  stock: StockTicker;
  onSelect: (stock: StockTicker) => void;
  isSelected: boolean;
}

export const StockCard: React.FC<Props> = ({ stock, onSelect, isSelected }) => {
  const trend = getTrendStatus(stock);
  const isUp = stock.changePct >= 0;

  return (
    <div 
      onClick={() => onSelect(stock)}
      className={`
        cursor-pointer p-4 rounded-xl border transition-all duration-200
        ${isSelected 
          ? 'bg-slate-800 border-blue-500 ring-1 ring-blue-500' 
          : 'bg-slate-800 border-slate-700 hover:border-slate-500 hover:bg-slate-750'}
      `}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            {stock.name} 
            <span className="text-sm font-normal text-slate-400">({stock.symbol})</span>
          </h3>
          <span className="text-xs text-slate-500 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
            {stock.sector}
          </span>
        </div>
        <div className="text-right">
          <div className={`text-lg font-bold ${isUp ? 'text-twRed' : 'text-twGreen'}`}>
            {stock.price}
          </div>
          <div className={`text-xs ${isUp ? 'text-twRed' : 'text-twGreen'}`}>
            {isUp ? '▲' : '▼'} {Math.abs(stock.changePct)}%
          </div>
        </div>
      </div>

      {/* Logic Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {trend === TrendStatus.BULLISH && (
          <span className="px-2 py-1 rounded text-[10px] font-bold bg-red-900/30 text-red-400 border border-red-900/50 flex items-center gap-1">
             <TrendingUp size={10} /> 趨勢多頭
          </span>
        )}
        {stock.vcp.stage2Confirmed && (
          <span className="px-2 py-1 rounded text-[10px] font-bold bg-blue-900/30 text-blue-400 border border-blue-900/50">
             Stage 2 確認
          </span>
        )}
        {stock.chips.foreignNetBuy > 0 && (
           <span className="px-2 py-1 rounded text-[10px] font-bold bg-purple-900/30 text-purple-400 border border-purple-900/50">
             外資買超
           </span>
        )}
      </div>

      {/* Trade Setup Grid */}
      <div className="grid grid-cols-2 gap-2 text-sm bg-slate-900/50 p-2 rounded-lg border border-slate-700/50 mb-3">
        <div className="flex flex-col">
           <span className="text-slate-500 text-[10px]">突破買點 (Pivot)</span>
           <span className="font-mono font-bold text-blue-400">{stock.vcp.pivotPrice}</span>
        </div>
        <div className="flex flex-col">
           <span className="text-slate-500 text-[10px]">止損 (Stop)</span>
           <span className="font-mono font-bold text-twGreen">{stock.vcp.stopLoss} (-5%)</span>
        </div>
        <div className="flex flex-col">
           <span className="text-slate-500 text-[10px]">目標 (Target)</span>
           <span className="font-mono font-bold text-twRed">{stock.vcp.target1} (+20%)</span>
        </div>
        <div className="flex flex-col">
           <span className="text-slate-500 text-[10px]">收縮次數 (Ts)</span>
           <span className="font-mono font-bold text-yellow-400">{stock.vcp.contractions}T</span>
        </div>
      </div>

      <div className="border-t border-slate-700 pt-2 mt-2">
        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
          <span className="text-blue-500 font-bold">分析:</span> {stock.reason}
        </p>
      </div>
    </div>
  );
};
