import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. 頁面設定 (必須放在第一行) ---
st.set_page_config(page_title="VCP Hunter Pro", layout="wide", page_icon="📈")

# --- 2. 核心邏輯：抓取資料 ---
@st.cache_data(ttl=60)
def fetch_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.TW")
        
        # 抓歷史資料 (畫圖用)
        df = ticker.history(period="1y")
        if df.empty: return None

        # 抓最新報價 (假日防護邏輯)
        current_price = 0.0
        try:
            intraday = ticker.history(period="5d", interval="1m")
            if not intraday.empty:
                current_price = float(intraday['Close'].iloc[-1])
            else:
                current_price = float(df['Close'].iloc[-1])
        except:
            current_price = float(df['Close'].iloc[-1])

        # 計算漲跌幅
        last_daily_close = float(df['Close'].iloc[-1])
        if abs(current_price - last_daily_close) < (current_price * 0.01):
            if len(df) >= 2:
                prev_close = float(df['Close'].iloc[-2])
            else:
                prev_close = last_daily_close
        else:
            prev_close = last_daily_close
            
        change_pct = round(((current_price - prev_close) / prev_close) * 100, 2)
        
        # 技術指標計算
        df['MA10'] = df['Close'].rolling(window=10).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        
        last_row = df.iloc[-1]
        recent_high = df['High'].tail(20).max()
        pivot = round(recent_high, 2)
        
        # 模擬外資/投信籌碼 (因為 yfinance 抓不到這個，這裡用隨機模擬展示 UI)
        # 實戰時建議接 FinMind 或 Fugle
        import random
        foreign_buy = random.randint(-500, 2000)
        trust_buy = random.randint(-200, 500)

        return {
            "symbol": symbol,
            "name": symbol, # 台股代號通常就是名字
            "price": round(current_price, 2),
            "changePct": change_pct,
            "pivot": pivot,
            "stopLoss": round(pivot * 0.94, 2), # 預設停損 -6%
            "target": round(pivot * 1.20, 2),   # 預設目標 +20%
            "volume": int(last_row['Volume']),
            "ma10": float(last_row['MA10']),
            "ma20": float(last_row['MA20']),
            "chips": {"foreign": foreign_buy, "trust": trust_buy},
            "df": df
        }
    except Exception as e:
        return None

# --- 3. UI 組件：風險計算機 ---
def risk_calculator(current_price, stop_loss, symbol):
    with st.container():
        st.markdown(f"#### 🧮 風險部位試算 ({symbol})")
        st.caption("依據「目前股價」與「止損價」之價差，計算建議倉位。")
        
        c1, c2 = st.columns(2)
        account_size = c1.number_input("總資金 (TWD)", value=100000, step=10000)
        risk_pct = c2.slider("單筆風險容忍 (%)", 0.5, 5.0, 2.0, 0.5)
        
        risk_amount = account_size * (risk_pct / 100)
        price_diff = current_price - stop_loss
        
        if price_diff > 0:
            suggested_shares = int(risk_amount / price_diff)
            position_value = suggested_shares * current_price
            
            # 結果顯示卡片
            st.info(f"""
            - **最大虧損金額**: ${int(risk_amount):,}
            - **建議買入股數**: **{suggested_shares:,} 股** ({suggested_shares/1000:.1f} 張)
            - **建議倉位總值**: ${int(position_value):,}
            """)
        else:
            st.warning("⚠️ 目前股價已低於止損價，不建議進場。")

# --- 4. 主程式介面 ---
st.title("🚀 VCP Hunter Pro")

# 初始化 session state (用來存追蹤清單)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# 側邊欄
with st.sidebar:
    st.header("⚙️ 策略設定")
    strategy = st.radio("選擇策略", ["標準 VCP (波段)", "Power Play (短線)"])
    
    if strategy == "Power Play (短線)":
        st.success("⚡ **Power Play 模式**\n\n趨勢 > 10MA > 20MA\n動能強勁，回檔極小")
    else:
        st.info("🌊 **標準 VCP 模式**\n\n趨勢 > 50MA > 200MA\n波動收縮，量縮整理")

    st.divider()
    user_input = st.text_area("輸入台股代號 (用逗號分隔)", "2330, 2317, 2454, 2603, 3231, 2618")
    
    # 顯示追蹤清單
    if st.session_state.watchlist:
        st.divider()
        st.subheader("⭐ 追蹤清單")
        for sym in st.session_state.watchlist:
            st.markdown(f"- **{sym}**")

# 主畫面邏輯
symbols = [s.strip() for s in user_input.split(",")]

if st.button("🔍 開始全市場掃描", use_container_width=True):
    progress = st.progress(0)
    
    for i, sym in enumerate(symbols):
        data = fetch_stock_data(sym)
        
        if data:
            # --- 判斷策略邏輯 (簡易版) ---
            is_match = False
            match_reason = ""
            
            if strategy == "Power Play (短線)":
                if data['price'] > data['ma10']:
                    is_match = True
                    match_reason = "🔥 強勢多頭 (站上10MA)"
                else:
                    match_reason = "尚未轉強"
            else:
                if data['price'] > data['ma20']: # 範例邏輯
                    is_match = True
                    match_reason = "✅ VCP 型態"
                else:
                    match_reason = "整理中"
            
            # --- 顯示卡片 (只顯示符合或全部，這裡為了演示顯示全部) ---
            with st.container():
                # 標題列
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.markdown(f"### {data['symbol']}")
                
                price_color = "red" if data['changePct'] >= 0 else "green"
                c2.markdown(f"<h3 style='color: {price_color}; text-align:right'>{data['price']}</h3>", unsafe_allow_html=True)
                c3.markdown(f"<p style='color: {price_color}; text-align:right; margin-top: 10px'>{data['changePct']}%</p>", unsafe_allow_html=True)
                
                # 標籤列
                st.caption(f"策略: {match_reason} | 產業: 電子 (模擬)")
                
                # 數據儀表板
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("外資 (模擬)", f"{data['chips']['foreign']}", delta_color="off")
                m2.metric("投信 (模擬)", f"{data['chips']['trust']}", delta_color="off")
                m3.metric("樞紐點", data['pivot'])
                m4.metric("成交量", f"{data['volume']:,}")
                
                # K 線圖
                df = data['df'].tail(60)
                fig = go.Figure(data=[go.Candlestick(x=df.index,
                                open=df['Open'], high=df['High'],
                                low=df['Low'], close=df['Close'], name="K線")])
                fig.add_trace(go.Scatter(x=df.index, y=df['MA10'], line=dict(color='orange', width=1), name='10MA'))
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='purple', width=1), name='20MA'))
                fig.update_layout(xaxis_rangeslider_visible=False, height=300, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # 功能區 (追蹤 & 風險計算)
                col_calc, col_btn = st.columns([3, 1])
                
                with col_calc:
                    with st.expander("🧮 開啟風險計算機"):
                        risk_calculator(data['price'], data['stopLoss'], data['symbol'])
                
                with col_btn:
                    # 追蹤按鈕邏輯
                    if data['symbol'] in st.session_state.watchlist:
                        if st.button("移除追蹤", key=f"remove_{data['symbol']}"):
                            st.session_state.watchlist.remove(data['symbol'])
                            st.rerun()
                    else:
                        if st.button("⭐ 加入", key=f"add_{data['symbol']}"):
                            st.session_state.watchlist.append(data['symbol'])
                            st.rerun()
                
                st.divider()

        progress.progress((i + 1) / len(symbols))

else:
    st.info("👈 請在左側輸入股票代號，並點擊「開始全市場掃描」")
