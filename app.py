import streamlit as st, pandas as pd, yfinance as yf
import plotly.graph_objects as go
st.set_page_config(layout="wide")
st.title("NSE 227 - BOX + Candles FIXED")

@st.cache_data(ttl=3600)
def load():
    try:
        df=pd.read_excel("All_227_Stocks_Financial_Analysis.xlsx")
        return df['Stock'].dropna().astype(str).tolist()
    except:
        return []

companies=load()
st.success(f"Loaded {len(companies)}")

TM={"Aadhar Hsg. Fin.":"AADHARHFC","Aarti Industries":"AARTIIND","Aavas Financiers":"AAVAS","ADF Foods":"ADFFOODS","Aditya Vision":"ADITYAVISION","Affle 3i":"AFFLE","Ajanta Pharma":"AJANTPHARM","Apar Industries":"APARINDS","APL Apollo Tubes":"APLAPOLLO","Apollo Hospitals":"APOLLOHOSP","Asian Paints":"ASIANPAINT","Avenue Supermarts":"DMART","Britannia Industries":"BRITANNIA","BSE":"BSE","Campus Activewear":"CAMPUS"}
def gt(c):
    c=c.strip()
    if c in TM: return TM[c]
    return c.split()[0][:10].upper()
tks=[gt(c) for c in companies]

def rsi(s):
    d=s.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    a=g.ewm(com=13, min_periods=14).mean(); b=l.ewm(com=13, min_periods=14).mean()
    return 100-(100/(1+a/b))

# NEW: Store full df for chart
@st.cache_data(ttl=600, show_spinner=False)
def fetch():
    rows=[]; charts={}
    for i in range(0,len(tks),20):
        batch=[f"{x}.NS" for x in tks[i:i+20]]
        comps=companies[i:i+20]; syms=tks[i:i+20]
        try:
            d=yf.download(batch, period="6mo", group_by='ticker', threads=False, progress=False, auto_adjust=True)
            for comp,sy,ns in zip(comps,syms,batch):
                try:
                    df = d if len(batch)==1 else (d[ns] if ns in d.columns.levels[0] else None)
                    if df is None or len(df.dropna())<30: continue
                    df=df.dropna()
                    lo=float(df['Low'].tail(20).min()); hi=float(df['High'].tail(20).max())
                    dL=lo*0.97; dH=lo*1.03; sL=hi*0.97; sH=hi*1.03
                    r=float(rsi(df['Close']).iloc[-1]); last=float(df['Close'].iloc[-1])
                    sig="HOLD"
                    if last<=dH*1.08 and r<52: sig="BUY"
                    elif last>=sL*0.92 and r>58: sig="SELL"
                    rows.append({"Stock":comp,"Ticker":sy,"CMP":round(last,1),"Support":round(lo,1),"Resistance":round(hi,1),"Demand BOX":f"{dL:.0f}-{dH:.0f}","Supply BOX":f"{sL:.0f}-{sH:.0f}","RSI":round(r,1),"Signal":sig,"_dL":dL,"_dH":dH,"_sL":sL,"_sH":sH})
                    charts[comp]=df.tail(90) # Keep last 90 days for chart
                except: continue
        except: continue
    return pd.DataFrame(rows), charts

live, chart_dict = fetch()

if live.empty:
    st.error("Yahoo blocked, try reboot")
else:
    sf=st.selectbox("Signal",["ALL","BUY","SELL","HOLD"])
    sr=st.text_input("Search")
    fl=live.copy()
    if sf!="ALL": fl=fl[fl['Signal']==sf]
    if sr: fl=fl[fl['Stock'].str.contains(sr, case=False)]
    st.dataframe(fl.drop(columns=["_dL","_dH","_sL","_sH"], errors='ignore'), use_container_width=True, height=350)
    st.caption(f"BUY:{len(live[live['Signal']=='BUY'])} SELL:{len(live[live['Signal']=='SELL'])} LIVE:{len(live)}/{len(companies)}")

    st.divider()
    sel=st.selectbox("Select Stock for Chart", fl['Stock'].tolist() if len(fl)>0 else live['Stock'].tolist())
    row=live[live['Stock']==sel].iloc[0]
    df=chart_dict.get(sel)

    if df is not None and not df.empty:
        fig=go.Figure()
        # Candles will now be in correct range because same df
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candles", increasing_line_color='#00FF00', decreasing_line_color='#FF0000', increasing_fillcolor='#00FF00', decreasing_fillcolor='#FF0000'))
        fig.add_hline(y=row['Support'], line_dash="dash", line_color="green", annotation_text=f"Sup {row['Support']}")
        fig.add_hline(y=row['Resistance'], line_dash="dash", line_color="red", annotation_text=f"Res {row['Resistance']}")
        # BOX across full chart width
        fig.add_shape(type="rect", x0=df.index[0], x1=df.index[-1], y0=row['_dL'], y1=row['_dH'], fillcolor="rgba(0,255,0,0.2)", line=dict(color="green", width=2))
        fig.add_shape(type="rect", x0=df.index[0], x1=df.index[-1], y0=row['_sL'], y1=row['_sH'], fillcolor="rgba(255,0,0,0.2)", line=dict(color="red", width=2))
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, title=f"{sel} - CMP {row['CMP']} - {row['Signal']} RSI {row['RSI']}", yaxis=dict(range=[row['_dL']*0.92, row['_sH']*1.08]))
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"Chart shows {len(df)} candles from {df.index[0].date()} to {df.index[-1].date()} - Demand Green BOX, Supply Red BOX")
    else:
        st.error("No chart data for this stock - Yahoo blocked, pick another stock")
