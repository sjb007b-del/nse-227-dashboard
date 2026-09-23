import streamlit as st
import pandas as pd
import yfinance as yf
import os
from datetime import datetime

st.set_page_config(page_title="NSE 227 - TradingView Pro", layout="wide")

st.markdown("<h2 style='text-align:center'>📈 TRADINGVIEW STYLE DASHBOARD</h2>", unsafe_allow_html=True)

# Timeframe selector
tf_map = {"Daily":"1d", "Weekly":"1wk", "Monthly":"1mo"}
tf_label = st.selectbox("Timeframe", ["Daily", "Weekly", "Monthly"])
interval = tf_map[tf_label]

# --- LOAD 227 STOCKS FROM EXCEL OR FALLBACK ---
@st.cache_data
def load_tickers():
    for fname in ["stocks.xlsx", "nse227.xlsx", "NSE227.xlsx"]:
        if os.path.exists(fname):
            try:
                df = pd.read_excel(fname)
                col = df.columns[0]
                for c in df.columns:
                    if "symbol" in c.lower() or "stock" in c.lower() or "name" in c.lower() or "ticker" in c.lower():
                        col = c
                        break
                tickers = df[col].astype(str).str.upper().str.strip().tolist()
                tickers = [t if ".NS" in t else f"{t}.NS" for t in tickers if t and t!='NAN']
                return tickers
            except: pass
    # Fallback 20 if excel not yet uploaded
    return ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","LT.NS","ITC.NS","KOTAKBANK.NS","BAJFINANCE.NS","HCLTECH.NS","ASIANPAINT.NS","AXISBANK.NS","MARUTI.NS","SUNPHARMA.NS","WIPRO.NS","ULTRACEMCO.NS","TITAN.NS","ONGC.NS","POWERGRID.NS","NTPC.NS","COALINDIA.NS","HINDUNILVR.NS","BAJAJFINSV.NS"]

tickers = load_tickers()

st.markdown(f"**TRADINGVIEW STYLE | {len(tickers)} STOCKS LOADED | {datetime.now().strftime('%d %b %Y %H:%M IST')} | NSE LIVE | {tf_label}**")
st.divider()

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(tickers_tuple, interval):
    data = []
    for sym in tickers_tuple:
        try:
            tk = yf.Ticker(sym)
            hist = tk.history(period="1y", interval=interval)
            if len(hist) < 5: continue
            last = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            chg = last - prev
            chgp = (chg/prev*100) if prev!=0 else 0
            high = float(hist['High'].iloc[-1])
            low = float(hist['Low'].iloc[-1])
            vol = int(hist['Volume'].iloc[-1])
            high52 = float(hist['High'].max())
            low52 = float(hist['Low'].min())
            ema20 = float(hist['Close'].ewm(span=20).mean().iloc[-1])
            # RSI
            delta = hist['Close'].diff()
            gain = delta.where(delta>0,0).rolling(14).mean()
            loss = -delta.where(delta<0,0).rolling(14).mean()
            rs = gain.iloc[-1]/(loss.iloc[-1]+1e-9)
            rsi = 100-(100/(1+rs)) if loss.iloc[-1]>0 else 60
            trend = "Bullish" if last > ema20 else "Bearish"

            data.append({
                "Name": sym.replace(".NS",""),
                "Last": round(last,2),
                "Chg": round(chg,2),
                "Chg%": round(chgp,2),
                "High": round(high,2),
                "Low": round(low,2),
                "Volume": vol,
                "52W High": round(high52,2),
                "52W Low": round(low52,2),
                "EMA 20": round(ema20,2),
                "RSI 14": round(rsi,1),
                "Trend": trend
            })
        except: continue
    return pd.DataFrame(data)

# Progress bar
bar = st.progress(0, text=f"Loading {len(tickers)} stocks - {tf_label}...")
df = fetch_data(tuple(tickers), interval)
bar.progress(100, text="Loaded!")
bar.empty()

if df.empty:
    st.error("No data. Check internet / try Reboot app")
else:
    df = df.sort_values("Chg%", ascending=False)

    # Filters like TradingView
    col1,col2,col3 = st.columns(3)
    with col1: trend_filter = st.multiselect("Filter Trend", ["Bullish","Bearish"])
    with col2: search = st.text_input("Search Symbol (e.g. RELIANCE)")
    with col3: min_vol = st.number_input("Min Volume", value=0)

    fdf = df.copy()
    if trend_filter: fdf = fdf[fdf["Trend"].isin(trend_filter)]
    if search: fdf = fdf[fdf["Name"].str.contains(search.upper(), na=False)]
    if min_vol>0: fdf = fdf[fdf["Volume"]>=min_vol]

    st.dataframe(fdf, use_container_width=True, hide_index=True)

    st.download_button("⬇️ Download CSV - All 227", fdf.to_csv(index=False), file_name="nse_227_tradingview.csv", mime="text/csv")

    st.caption(f"Showing {len(fdf)} / {len(df)} stocks | Excel not uploaded yet? Upload stocks.xlsx to repo to load all 227")
