import streamlit as st, pandas as pd, yfinance as yf
import plotly.graph_objects as go
st.set_page_config(layout="wide")
st.title("NSE 227 - BOX + Candles")

@st.cache_data(ttl=3600)
def load():
    try:
        df=pd.read_excel("All_227_Stocks_Financial_Analysis.xlsx")
        return df['Stock'].dropna().astype(str).tolist(), df
    except:
        return [], pd.DataFrame()

companies, mdf = load()
st.success(f"Loaded {len(companies)}")

TM={"Aadhar Hsg. Fin.":"AADHARHFC","Aarti Industries":"AARTIIND","Aavas Financiers":"AAVAS","ADF Foods":"ADFFOODS","Aditya Vision":"ADITYAVISION","Affle 3i":"AFFLE","Ajanta Pharma":"AJANTPHARM","Apar Industries":"APARINDS","APL Apollo Tubes":"APLAPOLLO","Apollo Hospitals":"APOLLOHOSP","Asian Paints":"ASIANPAINT","Avenue Supermarts":"DMART","Britannia Industries":"BRITANNIA","BSE":"BSE","Campus Activewear":"CAMPUS"}

def gt(c):
    c=c.strip()
    if c in TM: return TM[c]
    return c.split()[0][:10].upper()

tks=[gt(c) for c in companies]

def rsi(s):
    d=s.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    a=g.ewm(com=13, min_periods=14).mean()
    b=l.ewm(com=13, min_periods=14).mean()
    return 100-(100/(1+a/b))

def levels(df):
    if len(df)<20: return None
    lo=float(df['Low'].tail(20).min())
    hi=float(df['High'].tail(20).max())
    dL=lo*0.97; dH=lo*1.03; sL=hi*0.97; sH=hi*1.03
    r=float(rsi(df['Close']).iloc[-1]) if len(df)>14 else 50
    last=float(df['Close'].iloc[-1])
    sig="HOLD"; setup="Range"
    if last<=dH*1.05 and r<50: sig="BUY"; setup=f"Demand {dL:.0f}-{dH:.0f}"
    elif last>=sL*0.95 and r>55: sig="SELL"; setup=f"Supply {sL:.0f}-{sH:.0f}"
    return lo,hi,dL,dH,sL,sH,r,last,sig,setup

@st.cache_data(ttl=900)
def fetch():
    rows=[]
    for i in range(0,len(tks),30):
        batch=[f"{x}.NS" for x in tks[i:i+30]]
        comps=companies[i:i+30]; syms=tks[i:i+30]
        try:
            d=yf.download(batch, period="3mo", group_by='ticker', threads=False, progress=False, auto_adjust=True)
            for comp,sy,ns in zip(comps,syms,batch):
                try:
                    if len(batch)==1: df=d
                    else:
                        if ns in d.columns.levels[0]: df=d[ns]
                        else: continue
                    if df is None or len(df.dropna())<20: continue
                    df=df.dropna()
                    lo,hi,dL,dH,sL,sH,r,last,sig,setup=levels(df)
                    rows.append({"Stock":comp,"Ticker":sy,"CMP":round(last,1),"Support":round(lo,1),"Resistance":round(hi,1),"Demand BOX":f"{dL:.1f}-{dH:.1f}","Supply BOX":f"{sL:.1f}-{sH:.1f}","RSI":round(r,1),"Signal":sig,"Setup":setup,"_dL":dL,"_dH":dH,"_sL":sL,"_sH":sH})
                except: continue
        except: continue
    return pd.DataFrame(rows)

live=fetch()
if live.empty:
    st.warning("Yahoo busy"); st.dataframe(mdf)
else:
    sf=st.selectbox("Signal",["ALL","BUY","SELL","HOLD"])
    sr=st.text_input("Search")
    fl=live.copy()
    if sf!="ALL": fl=fl[fl['Signal']==sf]
    if sr: fl=fl[fl['Stock'].str.contains(sr, case=False)]
    st.dataframe(fl.drop(columns=["_dL","_dH","_sL","_sH"], errors='ignore'), use_container_width=True)
    st.write(f"BUY:{len(live[live['Signal']=='BUY'])} SELL:{len(live[live['Signal']=='SELL'])} LIVE:{len(live)}/{len(companies)}")
    st.divider()
    sel=st.selectbox("Select Stock for Chart", fl['Stock'].tolist() if len(fl)>0 else live['Stock'].tolist())
    row=live[live['Stock']==sel].iloc[0]
    df=yf.download(f"{row['Ticker']}.NS", period="3mo", progress=False, auto_adjust=True)
    if not df.empty:
        df=df.dropna()
        fig=go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candle", increasing_line_color='lime', decreasing_line_color='red'))
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='white', width=1), name="Close"))
        fig.add_hline(y=row['Support'], line_dash="dash", line_color="green")
        fig.add_hline(y=row['Resistance'], line_dash="dash", line_color="red")
        fig.add_shape(type="rect", x0=df.index[-20], x1=df.index[-1], y0=row['_dL'], y1=row['_dH'], fillcolor="rgba(0,255,0,0.2)", line=dict(color="green"))
        fig.add_shape(type="rect", x0=df.index[-20], x1=df.index[-1], y0=row['_sL'], y1=row['_sH'], fillcolor="rgba(255,0,0,0.2)", line=dict(color="red"))
        fig.update_layout(title=f"{sel} CMP {row['CMP']} {row['Signal']} RSI {row['RSI']}", xaxis_rangeslider_visible=False, height=500, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
