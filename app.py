import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="NSE 227 DEMA 9 LIVE", layout="wide", page_icon="📈")
st.title("📈 NSE 227 - DEMA 9 LIVE Dashboard")

def dema(series, period):
    ema1 = series.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    return 2*ema1 - ema2

@st.cache_data
def load_excel():
    try:
        return pd.read_excel("All_227_Stocks_Financial_Analysis.xlsx")
    except:
        return None

# Sidebar
sym = st.sidebar.text_input("NSE Symbol", "RELIANCE").upper().strip()
period = st.sidebar.selectbox("Period", ["1mo","3mo","6mo","1y","2y"], index=2)

yf_sym = sym if sym.endswith(".NS") else sym + ".NS"
st.sidebar.write(f"Loading: {yf_sym}")

try:
    df = yf.download(yf_sym, period=period, interval="1d", progress=False, auto_adjust=True)

    # Fix columns if MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if len(df) < 20:
        st.warning("Not enough data for this symbol")
    else:
        # Calculate DEMA 9, 20, 50, 200
        df['DEMA_9'] = dema(df['Close'], 9)
        df['DEMA_20'] = dema(df['Close'], 20)
        df['DEMA_50'] = dema(df['Close'], 50)
        df['DEMA_200'] = dema(df['Close'], 200)

        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        last_price = float(df['Close'].iloc[-1])
        last_dema9 = float(df['DEMA_9'].iloc[-1])
        last_dema20 = float(df['DEMA_20'].iloc[-1])
        last_rsi = float(df['RSI'].iloc[-1])

        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Price", f"₹{last_price:.2f}")
        col2.metric("DEMA 9", f"₹{last_dema9:.2f}", f"{last_price-last_dema9:.2f}")
        col3.metric("RSI 14", f"{last_rsi:.1f}")
        col4.metric("Trend", "BULLISH" if last_price > last_dema9 else "BEARISH")

        # Main Chart - Candlestick + DEMA 9
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="Candles"
        ))
        fig.add_trace(go.Scatter(x=df.index, y=df['DEMA_9'], mode='lines', line=dict(color='yellow', width=2.5), name='DEMA 9'))
        fig.add_trace(go.Scatter(x=df.index, y=df['DEMA_20'], mode='lines', line=dict(color='orange', width=1.5), name='DEMA 20'))
        fig.add_trace(go.Scatter(x=df.index, y=df['DEMA_50'], mode='lines', line=dict(color='#00BFFF', width=1.5), name='DEMA 50'))
        fig.add_trace(go.Scatter(x=df.index, y=df['DEMA_200'], mode='lines', line=dict(color='red', width=1.5), name='DEMA 200'))

        fig.update_layout(
            height=700, template="plotly_dark",
            xaxis_rangeslider_visible=False,
            title=f"{yf_sym} - DEMA 9 LIVE",
            legend=dict(orientation="h", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Volume Chart
        colors = ['#00ff88' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ff4444' for i in range(len(df))]
        fig_vol = go.Figure(data=[go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume")])pm

