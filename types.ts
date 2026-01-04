export enum TrendStatus {
  BULLISH = '多頭排列',
  BEARISH = '空頭排列',
  NEUTRAL = '整理中'
}

export interface StockCandle {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number; // In 'lots' (張)
  ma10?: number;
  ma20?: number;
  ma50?: number;
  ma150?: number;
  ma200?: number;
  volMa50?: number; // 50-day Volume MA for spike detection
}

export interface ChipData {
  foreignNetBuy: number; // 外資近5日買超
  trustNetBuy: number;   // 投信近5日買超
}

export interface Fundamentals {
  revenueYoy: number;    // 月營收年增率
  epsGrowth: number;     // 連續兩季EPS成長
}

export interface VcpData {
  contractions: number;  // Number of contractions detected (2-4)
  pivotPrice: number;    // Buy point
  stopLoss: number;      // 5-7% below pivot or technical low
  target1: number;       // +15-20%
  dryUpVolume: boolean;  // Is volume drying up before pivot?
  stage2Confirmed: boolean;
}

export interface StockTicker {
  symbol: string;
  name: string;
  price: number;
  changePct: number;
  sector: string;
  candles: StockCandle[];
  chips: ChipData;
  fundamentals: Fundamentals;
  vcp: VcpData;
  reason: string; // The "Analysis Summary" text
}

export interface WatchlistItem {
  symbol: string;
  alertPrice: number; // usually the stop loss or pivot retest level
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  timestamp: Date;
}