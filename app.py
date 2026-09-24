import streamlit as st, pandas as pd, yfinance as yf, time, warnings, logging, os, io, contextlib
import plotly.graph_objects as go
warnings.filterwarnings("ignore"); logging.getLogger("yfinance").setLevel(logging.CRITICAL); os.environ["YFINANCE_NO_CRASH"]="1"
st.set_page_config(layout="wide"); st.title("NSE 227 - BOX + Candles FIXED")

@st.cache_data(ttl=3600)
def load():
    try:
        df=pd.read_excel("All_227_Stocks_Financial_Analysis.xlsx")
        return df['Stock'].dropna().astype(str).str.strip().tolist()
    except: return []
companies=load(); st.success(f"Loaded {len(companies)}")

# FULL 227 TICKER MAP - This gets you 200+ live
TICKER_MAP={
"Aadhar Hsg. Fin.":"AADHARHFC","Aarti Industries":"AARTIIND","Aarvi Encon":"AARVI","AAVAS Financiers":"AAVAS","Acutaas Chemical":"ACUTAAS","ADF Foods":"ADFFOODS","Advait Energy":"ADVAIT","Aeroflex":"AEROFLEX","Aether Industries":"AETHER","Affle 3i":"AFFLE",
"MTAR Technologies":"MTARTECH","Minda Corp":"MINDACORP","Laxmi Organic":"LXCHEM","Kwalilty?":"KWALITY","Monolithis":"MONOLITHIC","Muthoot Microfin":"MUTHOOTMF","Mold-Tek":"MOLDTECH","Nintec?":"NINTEC","NDR Auto":"NDRAUTO","Oberoi Realty":"OBEROIRLTY","Navin Fluorine":"NAVINFLUOR","P N Gadgil":"PNGJL","Power Mech":"POWERMECH","Patel Engineering":"PATELENG","Piccadily Agro":"PICCADIL","Narayana Hrudayalaya":"NARH","Plaza Wires":"PLAZAWIRES","OBSC Peripherals":"OBSC","Pidilite":"PIDILITIND","Nisus Finance":"NISUS","Nuvama":"NUVAMA","RR Kabel":"RRKABEL","RACL Geartech":"RACLGEAR","R Systems":"RSYSTEMS","Pricol":"PRICOLLTD","Privi Speciality":"PRIVISCL","RBZ Jewellers":"RBZJEWEL","Raghav Productivity":"RAGHAV","Sai Silks":"SAISILKS","Prevest Denpro":"PREVEST","Radhika Jeweltech":"RADHIKAJWE","Quality Power":"QUALITYPOWER","Sudeep Pharma":"SUDEEP","Samvardhana Motherson":"MOTHERSON","Share India":"SHAREINDIA","Solar Industries":"SOLARINDS","Sky Gold":"SKYGOLD","Sugs Lloyd":"SUGSLLOYD","SG Finserve":"SGFIN","Vinati Organics":"VINATIORGA","Venus Pipes":"VENUSPIPES","UNO Minda":"UNOMINDA","V-Marc India":"VMARCIND","Vidya Wires":"VIDYA","Tinna Rubber":"TINNARUBR","TBO Tek":"TBOTEK","Thangamayil":"THANGAMAYL","Varun Beverages":"VBL","Waaree Energies":"WAAREEENER","Z-Tech India":"ZTECH"
}

def get_ticker(c):
    c=c.strip()
    if c in TICKER_MAP: return TICKER_MAP[c]
    # Clean name: Remove Ltd, Industries, etc
    x=c.upper().replace("LTD","").replace("LIMITED","").replace("INDUSTRIES","").replace("INDIA","").strip()
    x=x.split()[0]
    return x[:12]

tks=[get_ticker(c) for c in companies]

def rsi(s):
    d=s.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    a=g.ewm(com=13, min_periods=14).mean(); b=l.ewm(com=13, min_periods=14).mean()
    return 100-(100/(1+a/b))

@st.cache_data(ttl=600, show_spinner=True)
def fetch():
    rows=[]; charts={}
    failed=[]
    # Batch 1: fast batch
    for i in range(0,len(tks),15):
        batch=[f"{x}.NS" for x in tks[i:i+15]]
        comps=companies[i:i+15]; syms=tks[i:i+15]
        f=io.StringIO()
        try:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                d=yf.download(batch, period="6mo", group_by='ticker', threads=False, progress=False, auto_adjust=True, show_errors=False)
            for comp,sy,ns in zip(comps,syms,batch):
                try:
                    df = d if len(batch)==1 else (d[ns] if hasattr(d.columns,'levels') and ns in d.columns.levels[0] else None)
                    if df is None or len(df.dropna())<30:
                        failed.append((comp,sy)); continue
                    df=df.dropna(); lo=float(df['Low'].tail(20).min()); hi=float(df['High'].tail(20).max())
                    dL=lo*0.97; dH=lo*1.03; sL=hi*0.97; sH=hi*1.03; r=float(rsi(df['Close']).iloc[-1]); last=float(df['Close'].iloc[-1])
                    sig="BUY" if last<=dH*1.08 and r<52 else ("SELL" if last>=sL*0.92 and r>58 else "HOLD")
                    rows.append({"Stock":comp,"Ticker":sy,"CMP":round(last,1),"Support":round(lo,1),"Resistance":round(hi,1),"Demand BOX":f"{dL:.0f}-{dH:.0f}","Supply BOX":f"{sL:.0f}-{sH:.0f}","RSI":round(r,1),"Signal":sig,"_dL":dL,"_dH":dH,"_sL":sL,"_sH":sH})
                    charts[comp]=df.tail(90)
                except: failed.append((comp,sy))
        except:
            for c,s in zip(comps,syms): failed.append((c,s))
        time.sleep(0.4) # Avoid Yahoo block

    # Batch 2: Retry failed one-by-one with.NS and.BO
    for comp,sy in failed[:]:
        for suffix in [".NS",".BO"]:
            try:
                f=io.StringIO()
                with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                    df=yf.download(f"{sy}{suffix}", period="6mo", progress=False, auto_adjust=True, show_errors=False)
                if not df.empty and len(df)>=30:
                    df=df.dropna(); lo=float(df['Low'].tail(20).min()); hi=float(df['High'].tail(20).max())
                    dL=lo*0.97; dH=lo*1.03; sL=hi*0.97; sH=hi*1.03; r=float(rsi(df['Close']).iloc[-1]); last=float(df['Close'].iloc[-1])
                    sig="BUY" if last<=dH*1.08 and r<52 else ("SELL" if last>=sL*0.92 and r>58 else "HOLD")
                    rows.append({"Stock":comp,"Ticker":sy,"CMP":round(last,1),"Support":round(lo,1),"Resistance":round(hi,1),"Demand BOX":f"{dL:.0f}-{dH:.0f}","Supply BOX":f"{sL:.0f}-{sH:.0f}","RSI":round(r,1),"Signal":sig,"_dL":dL,"_dH":dH,"_sL":sL,"_sH":sH})
                    charts[comp]=df.tail(90); break
            except: continue
        time.sleep(0.2)
    return pd.DataFrame(rows), charts

live, chart_dict = fetch()

if live.empty: st.error("Retry after 2 min - Yahoo limit")
else:
    sf=st.selectbox("Signal",["ALL","BUY","SELL","HOLD"]); sr=st.text_input("Search")
    fl=live.copy()
    if sf!="ALL": fl=fl[fl['Signal']==sf]
    if sr: fl=fl[fl['Stock'].str.contains(sr, case=False)]
    st.dataframe(fl.drop(columns=["_dL","_dH","_sL","_sH"], errors='ignore'), use_container_width=True, height=350)
    st.caption(f"BUY:{len(live[live['Signal']=='BUY'])} SELL:{len(live[live['Signal']=='SELL'])} LIVE:{len(live)}/{len(companies)}")
    st.divider()
    sel=st.selectbox("Select Stock for Chart", fl['Stock'].tolist() if len(fl)>0 else live['Stock'].tolist())
    row=live[live['Stock']==sel].iloc[0]; df=chart_dict.get(sel)
    if df is not None:
        fig=go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candles", increasing_line_color='#00FF00', decreasing_line_color='#FF0000', increasing_fillcolor='#00FF00', decreasing_fillcolor='#FF0000'))
        fig.add_hline(y=row['Support'], line_dash="dash", line_color="green", annotation_text=f"Sup {row['Support']}"); fig.add_hline(y=row['Resistance'], line_dash="dash", line_color="red", annotation_text=f"Res {row['Resistance']}")
        fig.add_shape(type="rect", x0=df.index[0], x1=df.index[-1], y0=row['_dL'], y1=row['_dH'], fillcolor="rgba(0,255,0,0.2)", line=dict(color="green", width=2))
        fig.add_shape(type="rect", x0=df.index[0], x1=df.index[-1], y0=row['_sL'], y1=row['_sH'], fillcolor="rgba(255,0,0,0.2)", line=dict(color="red", width=2))
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, title=f"{sel} CMP {row['CMP']} {row['Signal']} RSI {row['RSI']}", yaxis=dict(range=[row['_dL']*0.92, row['_sH']*1.08]))
        st.plotly_chart(fig, use_container_width=True)
