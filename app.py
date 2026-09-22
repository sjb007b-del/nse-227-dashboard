import streamlit as st, yfinance as yf, pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="NSE 227 DEMA 9 PRO", layout="wide")
st.title("📈 NSE 227 - DEMA 9 LIVE | Demand Supply | Support Resistance")

NSE_227 = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","WIPRO.NS","HCLTECH.NS","ULTRACEMCO.NS","TITAN.NS","SUNPHARMA.NS","NESTLEIND.NS","POWERGRID.NS","NTPC.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","ADANIENT.NS","ADANIPORTS.NS","GRASIM.NS","HINDUNILVR.NS","BRITANNIA.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","BAJAJFINSV.NS","BAJAJ-AUTO.NS","EICHERMOT.NS","HEROMOTOCO.NS","M&M.NS","TECHM.NS","APOLLOHOSP.NS","BPCL.NS","INDUSINDBK.NS","VEDL.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIGI.NS","SHREECEM.NS","TATAPOWER.NS","TATAMOTORS.NS","DABUR.NS","PIDILITIND.NS","BERGEPAINT.NS","HAVELLS.NS","VOLTAS.NS","GODREJCP.NS","MARICO.NS","MUTHOOTFIN.NS","FEDERALBNK.NS","PNB.NS","BANKBARODA.NS","ZOMATO.NS","IRCTC.NS","HAL.NS","BEL.NS","DLF.NS","SIEMENS.NS","ABB.NS","POLYCAB.NS","BHARATFORG.NS","ASHOKLEY.NS","TVSMOTOR.NS","LTIM.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS","TATAELXSI.NS","NAUKRI.NS","LALPATHLAB.NS","BIOCON.NS","LUPIN.NS","AUROPHARMA.NS","SRF.NS","DIXON.NS","VBL.NS","TRENT.NS","DMART.NS","CHOLAFIN.NS","SHRIRAMFIN.NS","PFC.NS","RECLTD.NS","SAIL.NS","NMDC.NS"]

def dema(s, p):
    e1=s.ewm(span=p, adjust=False).mean()
    e2=e1.ewm(span=p, adjust=False).mean()
    return 2*e1-e2

symbol = st.sidebar.selectbox("Select Stock (227)", sorted(set(NSE_227)), index=0)
period = st.sidebar.selectbox("Period", ["3mo","6mo","1y","2y"], index=2)

@st.cache_data(ttl=300)
def load_data(sym, per):
    df = yf.download(sym, period=per, interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

df = load_data(symbol, period)

if df.empty:
    st.error("Data not loaded. Try another stock.")
else:
    close = df['Close']
    df['DEMA9'] = dema(close, 9)
    df['DEMA20'] = dema(close, 20)
    df['DEMA50'] = dema(close, 50)
    df['DEMA200'] = dema(close, 200)
    df['Support'] = df['Low'].rolling(15).min()
    df['Resistance'] = df['High'].rolling(15).max()
    
    last = df.iloc[-1]
    price = float(last['Close'])
    s_val = float(last['Support'])
    r_val = float(last['Resistance'])
    d9_val = float(last['DEMA9'])

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("LTP", f"{price:.2f}")
    c2.metric("DEMA 9", f"{d9_val:.2f}")
    c3.metric("DEMA 200", f"{float(last['DEMA200']):.2f}")
    c4.metric("Support", f"{s_val:.2f}")
    c5.metric("Resistance", f"{r_val:.2f}")

    demand_low = df['Low'].tail(30).min()
    demand_high = demand_low * 1.03
    supply_high = df['High'].tail(30).max()
    supply_low = supply_high * 0.97

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['DEMA9'], name="DEMA 9", line=dict(color="#FFFF00", width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['DEMA20'], name="DEMA 20", line=dict(color="#FFA500")))
    fig.add_trace(go.Scatter(x=df.index, y=df['DEMA50'], name="DEMA 50", line=dict(color="#00FFFF")))
    fig.add_trace(go.Scatter(x=df.index, y=df['DEMA200'], name="DEMA 200", line=dict(color="#FF0000")))
    fig.add_trace(go.Scatter(x=df.index, y=df['Support'], name="Support", line=dict(color="#00FF00", dash="dash")))
    fig.add_trace(go.Scatter(x=df.index, y=df['Resistance'], name="Resistance", line=dict(color="#FF4444", dash="dash")))
    
    fig.add_hrect(y0=demand_low, y1=demand_high, fillcolor="green", opacity=0.15, line_width=0, annotation_text="DEMAND ZONE")
    fig.add_hrect(y0=supply_low, y1=supply_high, fillcolor="red", opacity=0.15, line_width=0, annotation_text="SUPPLY ZONE")

    fig.update_layout(template="plotly_dark", height=650, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    if price > d9_val and price > float(last['DEMA20']):
        st.success(f"BUY - {symbol} above DEMA 9 & 20 | Demand Zone {demand_low:.2f}")
    elif price < d9_val:
        st.error(f"SELL - {symbol} below DEMA 9 | Supply Zone {supply_high:.2f} | Support {s_val:.2f}")
    else:
        st.warning(f"SIDEWAYS - {symbol} around DEMA 9")

st.sidebar.info("Final Version - 227 stocks, Demand/Supply, Support/Resistance")
