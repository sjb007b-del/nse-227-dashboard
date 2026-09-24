import streamlit as st, pandas as pd, yfinance as yf
import plotly.graph_objects as go
st.set_page_config(layout="wide")
st.title("NSE 227 - BOX Chart with Candles")

@st.cache_data(ttl=3600)
def load_stocks():
    try:
        df=pd.read_excel("All_227_Stocks_Financial_Analysis.xlsx")
        return df['Stock'].dropna().astype(str).str.strip().tolist(), df
    except:
        return [], pd.DataFrame()

companies, master_df = load_stocks()
st.success(f"Loaded {len(companies)} stocks")

TICKER_MAP={"Aadhar Hsg. Fin.":"AADHARHFC","Aarti Industries":"AARTIIND","Aavas Financiers":"AAVAS","ADF Foods":"ADFFOODS","Aditya Vision":"ADITYAVISION","Affle 3i":"AFFLE","Ajanta Pharma":"AJANTPHARM","Apar Industries":"APARINDS","APL Apollo Tubes":"APLAPOLLO","Apollo Hospitals":"APOLLOHOSP","Asian Paints":"ASIANPAINT","Avenue Supermarts":"DMART","Britannia Industries":"BRITANNIA","BSE":"BSE","Campus Activewear":"CAMPUS"}
def get_ticker(c):
    c=c.strip()
    if c in TICKER_MAP: return TICKER_MAP[c]
    return c.upper().split()[0][:10]
tickers=[get_ticker(c) for c in companies]

def rsi_calc(close, p=14):
    d=close.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    ag=g.ewm(com=p-1, min_periods=p).mean(); al=l.ewm(com=p-1, min_periods=p).mean()
    return 100-(100/(1+ag/al))

def calc_levels(df):
    if len(df)<20: return None
    close=df['Close']; low=df['Low']; high=df['High']
    sup=float(low.tail(20).min()); res=float(high.tail(20).max())
    dL=sup*0.97; dH=sup*1.03; sL=res*0.97; sH=res*1.03
    r=float(rsi_calc(close).iloc[-1]) if len(close)>14 else 50
    last=float(close.iloc[-1]); sig="HOLD"; setup="Range"
    if last<=dH*1.05 and r<50: sig="BUY"; setup=f"Demand {dL:.0f}-{dH:.0f}"
    elif last>=sL*0.95 and r>55: sig="SELL"; setup=f"Supply {sL:.0f}-{sH:.0f}"
    return {"Sup":sup,"Res":res,"dL":dL,"dH":dH,"sL":sL,"sH":sH,"DZ":f"{dL:.1f}-{dH:.1f}","SZ":f"{sL:.1f}-{sH:.1f}","RSI":round(r,1),"Last":round(last,2),"Sig":sig,"Setup":setup}

@st.cache_data(ttl=900)
def fetch_all(tickers
