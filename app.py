import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="NSE 227 DEMA 9 LIVE", layout="wide")
st.title("NSE 227 - DEMA 9 LIVE")

def dema(s, p):
    e1 = s.ewm(span=p, adjust=False).mean()
    e2 = e1.ewm(span=p, adjust=False).mean()
    return 2*e1 - e2

sym = st.sidebar.text_input("Symbol", "RELIANCE").upper().strip()
per = st.sidebar.selectbox("Period", ["1mo","3mo","6mo","1y"], 2)
yf_sym = sym if sym.endswith(".NS") else sym + ".NS"

df = yf.download(yf_sym, period=per, interval="1d", progress=False, auto_adjust=True)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

if len(df) > 0:
    df['DEMA9'] = dema(df['Close'], 9)
    df['DEMA20'] = dema(df['Close'], 20)
    df['DEMA50'] = dema(df['Close'], 50)
    df['DEMA200'] = dema(df['Close'], 200)

    last = float(df['Close'].iloc[-1])
    d9 = float(df['DEMA9'].iloc[-1])

    c1, c2 = st.columns(2)
    c1.metric("Price", f"{last:.2f}")
    c2.metric("DEMA9", f"{d9:.2f}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['DEMA9'], line=dict(color='yellow', width=2), name='DEMA 9'))
    fig.add_trace(go.Scatter(x=df.index, y=df['DEMA20'], line=dict(color='orange'), name='DEMA 20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['DEMA50'], line=dict(color='cyan'), name='DEMA 50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['DEMA200'], line=dict(color='red'), name='DEMA 200'))
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume"))
    fig2.update_layout(height=200, template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

    if last > d9:
        st.success("BULLISH - Above DEMA 9")
    else:
        st.error("BEARISH - Below DEMA 9")
else:
    st.error("No data")
