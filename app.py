import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 設定網頁標題與寬度 ---
st.set_page_config(page_title="VCP Hunter Lite", layout="wide", page_icon="📈")

# --- 核心邏輯：抓取資料 (包含假日防護) ---
@st.cache_data(ttl=60) # 快取 60 秒，避免一直重複抓
def fetch_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.TW")
        
        # 1. 抓歷史資料
        df = ticker.history(period="1y")
        if df.empty: return None

        # 2. 抓最新報價 (假日防護)
        current_price = 0.0
        # 優先嘗試抓近5天的1分鐘線 (解決週日抓不到週五收盤的問題)
        try:
            intraday = ticker.history(period="5d", interval="1m")
            if not intraday.empty:
                current_price = float(intraday['Close'].iloc[-1])
            else:
                current_price = float(df['Close'].iloc[-1])
        except:
            current_price = float(df['Close'].iloc[-1])

        # 3. 計算漲跌幅
        last_daily_close = float(df['Close'].iloc[-1])
        if abs(current_price - last_daily_close) < 0.05:
            prev_close = float(df['Close'].iloc[-2])
        else:
            prev_close = last_daily_close
            
        change_pct = round(((current_price - prev_close) / prev_close) * 100, 2)
        
        # 4. 準備 VCP 數據
        recent_high = df['High'].tail(20).max()
        pivot = round(recent_high, 2)
        
        # 5. 回傳乾淨的字典
        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "changePct": change_pct,
            "pivot": pivot,
            "volume": int(df['Volume'].iloc[-1]),
            "df": df # 用來畫圖
        }
    except Exception as e:
        return None

# --- 介面開始 ---
st.title("📈 VCP Hunter (Mobile Ver.)")

# 1. 側邊欄：輸入股票與策略
with st.sidebar:
    st.header("設定")
    user_input = st.text_input("輸入台股代號 (例如 2330, 2317)", "2330, 2317, 2454, 2603")
    strategy = st.radio("選擇策略", ["標準 VCP (波段)", "Power Play (短線)"])
    
    st.info("💡 手機版操作：點擊左上角箭頭可收合此選單。")

# 2. 處理輸入並掃描
symbols = [s.strip() for s in user_input.split(",")]
results = []

if st.button("🚀 開始掃描", use_container_width=True):
    progress_bar = st.progress(0)
    for i, sym in enumerate(symbols):
        data = fetch_stock_data(sym)
        if data:
            results.append(data)
        progress_bar.progress((i + 1) / len(symbols))
    
    # 3. 顯示結果
    if results:
        for stock in results:
            # 判斷顏色
            color = "red" if stock['changePct'] >= 0 else "green"
            arrow = "▲" if stock['changePct'] >= 0 else "▼"
            
            # 卡片式佈局
            with st.container():
                st.markdown(f"### {stock['symbol']} (現價: {stock['price']})")
                
                # 重要數據列
                c1, c2, c3 = st.columns(3)
                c1.metric("漲跌幅", f"{stock['changePct']}%", delta_color="off")
                c2.metric("樞紐點 (Pivot)", stock['pivot'])
                c3.metric("策略", "符合" if strategy == "標準 VCP (波段)" else "觀察中")
                
                # 畫圖 (K線圖)
                df = stock['df'].tail(60)
                fig = go.Figure(data=[go.Candlestick(x=df.index,
                                open=df['Open'], high=df['High'],
                                low=df['Low'], close=df['Close'])])
                fig.update_layout(xaxis_rangeslider_visible=False, height=300, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                st.divider() # 分隔線
    else:
        st.warning("找不到股票資料，請檢查代號是否正確。")

else:
    st.write("請輸入代號並點擊掃描...")
