import streamlit as st, pandas as pd, yfinance as yf
import plotly.graph_objects as go
st.set_page_config(layout="wide")
st.title("NSE 227 - Demand-Supply BOX Chart + S/R + BUY/SELL")

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
def fetch_all(tickers, companies):
    rows=[]
    for i in range(0,len(tickers),30):
        batch=[f"{t}.NS" for t in tickers[i:i+30]]; batch_bo=[f"{t}.BO" for t in tickers[i:i+30]]
        comps=companies[i:i+30]; tks=tickers[i:i+30]
        try:
            d_ns=yf.download(batch, period="3mo", group_by='ticker', threads=False, progress=False, auto_adjust=True)
            d_bo=yf.download(batch_bo, period="3mo", group_by='ticker', threads=False, progress=False, auto_adjust=True)
            for comp,t,ns,bo in zip(comps,tks,batch,batch_bo):
                df=None
                try:
                    if len(batch)==1: df=d_ns if not d_ns.empty else d_bo
                    else:
                        if ns in d_ns.columns.levels[0] and len(d_ns[ns].dropna())>10: df=d_ns[ns]
                        elif bo in d_bo.columns.levels[0]: df=d_bo[bo]
                    if df is None or len(df.dropna())<20: continue
                    df=df.dropna(); lev=calc_levels(df)
                    if not lev: continue
                    rows.append({"Stock":comp,"Ticker":t,"CMP":lev['Last'],"Support":round(lev['Sup'],1),"Resistance":round(lev['Res'],1),"Demand BOX":lev['DZ'],"Supply BOX":lev['SZ'],"RSI":lev['RSI'],"Signal":lev['Sig'],"Setup":lev['Setup'],"_dL":lev['dL'],"_dH":lev['dH'],"_sL":lev['sL'],"_sH":lev['sH']})
                except: continue
        except: continue
    return pd.DataFrame(rows)

with st.spinner("Fetching LIVE 227..."):
    live_df=fetch_all(tickers, companies)

if live_df.empty:
    st.warning("Yahoo blocked, reboot after 2 min"); st.dataframe(master_df)
else:
    c1,c2,c3=st.columns(3)
    with c1: sf=st.selectbox("Signal",["ALL","BUY","SELL","HOLD"])
    with c2: rs=st.slider("RSI Max BUY",30,70,55)
    with c3: sr=st.text_input("Search")
    fl=live_df.copy()
    if sf!="ALL": fl=fl[fl['Signal']==sf]
    if sr: fl=fl[fl['Stock'].str.contains(sr, case=False)]
    if sf=="BUY": fl=fl[fl['RSI']<=rs]
    st.dataframe(fl.drop(columns=["_dL","_dH","_sL","_sH"], errors='ignore'), use_container_width=True, height=400)
    st.write(f"BUY:{len(live_df[live_df['Signal']=='BUY'])} SELL:{len(live_df[live_df['Signal']=='SELL'])} LIVE:{len(live_df)}/{len(companies)}")
    st.divider(); st.subheader("📦 BOX Chart")
    sel=st.selectbox("Select Stock", fl['Stock'].tolist() if len(fl)>0 else live_df['Stock'].tolist())
    row=live_df[live_df['Stock']==sel].iloc[0]
    @st.cache_data(ttl=900)
    def get_chart(tk):
        for suf in [".NS",".BO"]:
            try:
                df=yf.download(f"{tk}{suf}", period="3mo", progress=False, auto_adjust=True)
                if not df.empty and len(df)>20: return df
            except: continue
        return pd.DataFrame()
    cdf=get_chart(row['Ticker'])
    if not cdf.empty:
        fig=go.Figure(); fig.add_trace(go.Candlestick(x=cdf.index, open=cdf['Open'], high=cdf['High'], low=cdf['Low'], close=cdf['Close'], name="Price"))
        fig.add_hline(y=row['Support'], line_dash="dash", line_color="green", annotation_text=f"Sup {row['Support']}")
        fig.add_hline(y=row['Resistance'], line_dash="dash", line_color="red", annotation_text=f"Res {row['Resistance']}")
        fig.add_shape(type="rect", x0=cdf.index[-30], x1=cdf.index[-1], y0=row['_dL'], y1=row['_dH'], fillcolor="rgba(0,255,0,0.2)", line=dict(color="green",width=2))
        fig.add_shape(type="rect", x0=cdf.index[-30], x1=cdf.index[-1], y0=row['_sL'], y1=row['_sH'], fillcolor="rgba(255,0,0,0.2)", line=dict(color="red",width=2))
        fig.update_layout(title=f"{sel} CMP:{row['CMP']} {row['Signal']} RSI:{row['RSI']} {row['Setup']}", xaxis_rangeslider_visible=False, height=500, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.code(f"Green BOX (BUY): {row['Demand BOX']}\nRed BOX (SELL): {row['Supply BOX']}")
    st.download_button("Download CSV", live_df.to_csv(index=False), "NSE_227_BOX.csv")
