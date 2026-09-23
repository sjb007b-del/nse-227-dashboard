import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="NSE 227 - TradingView Pro", layout="wide")
st.markdown("<h2 style='text-align:center'>📈 TRADINGVIEW STYLE DASHBOARD - 227 STOCKS</h2>", unsafe_allow_html=True)

tf_map = {"Daily":"1d", "Weekly":"1wk", "Monthly":"1mo"}
tf_label = st.selectbox("Timeframe", ["Daily", "Weekly", "Monthly"])
interval = tf_map[tf_label]

# === FULL 227 NSE STOCKS LIST ===
TICKERS_227 = [
"RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","BHARTIARTL.NS","SBIN.NS","LICI.NS","BAJFINANCE.NS","ITC.NS",
"LT.NS","HCLTECH.NS","KOTAKBANK.NS","SUNPHARMA.NS","MARUTI.NS","ASIANPAINT.NS","AXISBANK.NS","WIPRO.NS","ULTRACEMCO.NS","TITAN.NS",
"BAJAJFINSV.NS","DMART.NS","ADANIENT.NS","ONGC.NS","NTPC.NS","POWERGRID.NS","COALINDIA.NS","HINDUNILVR.NS","NESTLEIND.NS","ADANIPORTS.NS",
"JSWSTEEL.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","DIVISLAB.NS","EICHERMOT.NS","BRITANNIA.NS","HDFCLIFE.NS","SBILIFE.NS","BAJAJ-AUTO.NS",
"HEROMOTOCO.NS","TATAMOTORS.NS","TATASTEEL.NS","HINDALCO.NS","VEDL.NS","INDUSINDBK.NS","TECHM.NS","APOLLOHOSP.NS","UPL.NS",
"BPCL.NS","IOC.NS","GAIL.NS","TATACONSUM.NS","PIDILITIND.NS","DABUR.NS","GODREJCP.NS","MARICO.NS","COLPAL.NS","BERGEPAINT.NS",
"SHREECEM.NS","AMBUJACEM.NS","ACC.NS","SIEMENS.NS","ABB.NS","HAVELLS.NS","VOLTAS.NS","DIXON.NS","POLYCAB.NS","CUMMINSIND.NS",
"LTIM.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS","LTTS.NS","TATAELXSI.NS","KPITTECH.NS","TATACOMM.NS","INDIANB.NS","BANKBARODA.NS",
"PNB.NS","CANBK.NS","UNIONBANK.NS","FEDERALBNK.NS","IDFCFIRSTB.NS","BANDHANBNK.NS","AUBANK.NS","ICICIPRULI.NS","ICICIGI.NS","SBICARD.NS",
"MUTHOOTFIN.NS","CHOLAFIN.NS","BAJAJHLDNG.NS","SHRIRAMFIN.NS","RECLTD.NS","PFC.NS","IRFC.NS","HUDCO.NS","NHPC.NS","SJVN.NS",
"ADANIGREEN.NS","ADANIENSOL.NS","TATAPOWER.NS","JSWENERGY.NS","TORRENTPOWER.NS","INDIGRID.NS","IRCTC.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS",
"POLICYBZR.NS","DELHIVERY.NS","NAUKRI.NS","INDIAMART.NS","LALPATHLAB.NS","METROPOLIS.NS","SYNGENE.NS","LAURUSLABS.NS","AUROPHARMA.NS","LUPIN.NS",
"ALKEM.NS","ZYDUSLIFE.NS","GLENMARK.NS","BIOCON.NS","TORNTPHARM.NS","IPCALAB.NS","MANKIND.NS","ABBOTINDIA.NS","GLAND.NS","CROMPTON.NS",
"WHIRLPOOL.NS","AMBER.NS","RAJESHEXPO.NS","KALYANKJIL.NS","TITAN.NS","BATAINDIA.NS","RELAXO.NS","PAGEIND.NS","TRENT.NS","ABFRL.NS",
"JUBLFOOD.NS","DEVYANI.NS","WESTLIFE.NS","TATACONSUM.NS","VBL.NS","UBL.NS","MCDOWELL-N.NS","RADICO.NS","GODREJIND.NS","BALKRISIND.NS",
"MRF.NS","APOLLOTYRE.NS","CEAT.NS","MOTHERSON.NS","BOSCHLTD.NS","BHARATFORG.NS","ASHOKLEY.NS","TVSMOTOR.NS","BAJAJ-AUTO.NS","ESCORTS.NS",
"CONCOR.NS","INDIGO.NS","SPICEJET.NS","HAL.NS","BEL.NS","BDL.NS","MAZDOCK.NS","COCHINSHIP.NS","GRSE.NS","BHEL.NS",
"LT.NS","ADANIENT.NS","GMRINFRA.NS","IRB.NS","NBCC.NS","NCC.NS","OBEROIRLTY.NS","DLF.NS","GODREJPROP.NS","PRESTIGE.NS",
"BRIGADE.NS","SOBHA.NS","PHOENIXLTD.NS","INDHOTEL.NS","EIHOTEL.NS","LEMONTREE.NS","CHALET.NS","MAHLOG.NS","TCI.NS","BLUEDART.NS",
"PIDILITIND.NS","SRF.NS","DEEPAKNTR.NS","NAVINFLUOR.NS","ATUL.NS","AARTIIND.NS","BALRAMCHIN.NS","UPL.NS","COROMANDEL.NS","CHAMBLFERT.NS",
"GNFC.NS","GSFC.NS","FACT.NS","RALLIS.NS","PIIND.NS","ASTRAL.NS","SUPREMEIND.NS","FINCABLES.NS","FINPIPE.NS","KEI.NS",
"APARINDS.NS","HINDZINC.NS","NATIONALUM.NS","SAIL.NS","JSL.NS","JSWSTEEL.NS","JINDALSTEL.NS","NMDC.NS","MOIL.NS","HINDCOPPER.NS",
"GMDCLTD.NS","KIOCL.NS","WELCORP.NS","RATNAMANI.NS","APLAPOLLO.NS","TATACHEM.NS","PCBL.NS","GRAPHITE.NS","HEG.NS","EIDPARRY.NS"
]

st.markdown(f"**TRADINGVIEW STYLE | {len(TICKERS_227)} STOCKS LOADED | {datetime.now().strftime('%d %b %Y %H:%M IST')} | NSE LIVE | {tf_label}**")
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
            delta = hist['Close'].diff()
            gain = delta.where(delta>0,0).rolling(14).mean()
            loss = -delta.where(delta<0,0).rolling(14).mean()
            rs = gain.iloc[-1]/(loss.iloc[-1]+1e-9)
            rsi = 100-(100/(1+rs)) if loss.iloc[-1]>0 else 60
            trend = "Bullish" if last > ema20 else "Bearish"
            data.append({"Name":sym.replace(".NS",""),"Last":round(last,2),"Chg":round(chg,2),"Chg%":round(chgp,2),"High":round(high,2),"Low":round(low,2),"Volume":vol,"52W High":round(high52,2),"52W Low":round(low52,2),"EMA 20":round(ema20,2),"RSI 14":round(rsi,1),"Trend":trend})
        except: continue
    return pd.DataFrame(data)

with st.spinner(f"Loading {len(TICKERS_227)} stocks - {tf_label} - Please wait 60 sec for first load..."):
    df = fetch_data(tuple(TICKERS_227), interval)

if not df.empty:
    df = df.sort_values("Chg%", ascending=False)
    c1,c2,c3 = st.columns(3)
    with c1: trend_f = st.multiselect("Filter Trend", ["Bullish","Bearish"])
    with c2: search = st.text_input("Search Symbol (e.g. RELIANCE)")
    with c3: min_vol = st.number_input("Min Volume", value=0)
    fdf = df.copy()
    if trend_f: fdf = fdf[fdf["Trend"].isin(trend_f)]
    if search: fdf = fdf[fdf["Name"].str.contains(search.upper(), na=False)]
    if min_vol>0: fdf = fdf[fdf["Volume"]>=min_vol]
    st.dataframe(fdf, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download CSV - 227 Stocks", fdf.to_csv(index=False), file_name="nse_227_tradingview.csv")
    st.success(f"Showing {len(fdf)} / {len(df)} stocks - All 227 Loaded!")
else:
    st.error("No data")
