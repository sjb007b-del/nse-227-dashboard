import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go, glob
from datetime import datetime

st.set_page_config(layout="wide", page_title="NSE 227 TradingView PRO")
# === TRADINGVIEW CSS ===
st.markdown("""
<style>
header {visibility:hidden;}
.block-container {padding-top:0.5rem;}
[data-testid="stMetricValue"] {font-size:18px;}
.watchlist {background:#131722; border-left:1px solid #2a2e39; padding:10px;}
</style>
""", unsafe_allow_html=True)

# === YOUR 227 MAP ===
NSE_MAP = {
"Aadhar Hsg. Fin.": "AADHARHFC.NS","Aarti Industries": "AARTIIND.NS","Aarti Surfactant": "AARTISURF.NS","Aarvi Encon": "AARVI.NS","AAVAS Financiers": "AAVAS.NS","Acutaas Chemical": "ACUTAAS.NS","ADF Foods": "ADFFOODS.NS","Aditya Infotech": "ADITYAINF.NS","Aditya Vision": "AVL.NS","Advait Energy": "ADVAIENT.NS","Aeroflex": "AEROFLEX.NS","Aether Industries": "AETHER.NS","Afcom Holdings": "AFCOM.NS","Affle 3i": "AFFLE.NS","AGI Infra": "AGI.NS","Ajanta Pharma": "AJANTPHARM.NS","Alpex Solar": "ALPEXSOLAR.NS","Anand Rathi Share": "ANANDRATHI.NS","Anand Rathi Wealth": "ANANDRATHI.NS","Anant Raj": "ANANTRAJ.NS","Anlon Healthcare": "ANLON.NS","Anupam Rasayan": "ANURAS.NS","Apar Industries": "APARINDS.NS","APL Apollo Tubes": "APLAPOLLO.NS","Apollo Hospitals": "APOLLOHOSP.NS","Apollo Micro Systems": "APOLLO.NS","Aptus Value Housing": "APTUS.NS","Arman Financial": "ARMANFIN.NS","Artemis Medicare": "ARTEMISMED.NS","Asarfi Hospital": "ASARFI.NS","Asian Paints": "ASIANPAINT.NS","ASK Automotive": "ASKAUTOLTD.NS","ASM Technologies": "ASMTEC.NS","Astral": "ASTRAL.NS","Atlanta Electric": "ATLANTA.NS","Avalon Technologies": "AVALON.NS","Avenue Supermarts": "DMART.NS","Azad Engineering": "AZAD.NS","Bajaj Finance": "BAJFINANCE.NS","Bajaj Housing Finance": "BAJAJHFL.NS","Balu Forge": "BALUFORGE.NS","Bansal Roofing": "BANSALROOF.NS","Bharat Dynamics": "BDL.NS","Bharat Electronics": "BEL.NS","Bharat Seats": "BHARATSEAT.NS","BLS E-Services": "BLSE.NS","BLS International": "BLS.NS","Blue Water": "BLUEWATER.NS","Bondada Engineering": "BONDADA.NS","Borana Weaves": "BORANAWV.NS","Britannia Industries": "BRITANNIA.NS","BSE": "BSE.NS","Campus Activewear": "CAMPUS.NS","Can Fin Homes": "CANFINHOME.NS","CarTrade Tech": "CARTRADE.NS","Ceinsys Tech": "CEINSYSTECH.NS","Cellecor Gadgets": "CELLECOR.NS","CFF Fluid Control": "CFF.NS","CG Power & Industrial": "CGPOWER.NS","Chandan Healthcare": "CHANDAN.NS","Choice International": "CHOICEIN.NS","Craftsman Automation": "CRAFTSMAN.NS","CRISIL": "CRISIL.NS","Cupid": "CUPID.NS","D.P. Abhushan": "DPABHUSHAN.NS","Danish Power": "DANISH.NS","Data Patterns": "DATAPATTNS.NS","DC Infotech": "DCINFOTEC.NS","DEE Development": "DEEDEV.NS","Deep Industries": "DEEPINDS.NS","Delton Cables": "DELTON.NS","Divgi TorqTransfer": "DIVGIITTS.NS","DRC Systems": "DRCSYSTEMS.NS","Dynamic Cables": "DYCL.NS","Eicher Motors": "EICHERMOT.NS","Emmvee Photovoltaic": "EMMVEE.NS","eMudhra": "EMUDHRA.NS","Entero Healthcare": "ENTERO.NS","EPACK Prefab Technologies": "EPACK.NS","Ethos": "ETHOSLTD.NS","Exhicon Events": "EXHICON.NS","Fabtech Technologies": "FABTECH.NS","Finolex Cables": "FINCABLES.NS","Fredun Pharma": "FREDUN.NS","Fujiyama Power": "FUJIYAMA.NS","Gala Precision Engineering": "GALAPREC.NS","Gandhar Oil Refinery": "GANDHAR.NS","Ganesh Green": "GANESHGREEN.NS","Garden Reach Shipbuilders": "GRSE.NS","Garuda Construction": "GARUDA.NS","GK Energy": "GKENERGY.NS","Gland Pharma": "GLAND.NS","Global Health": "MEDANTA.NS","GNG Electronics": "GNG.NS","Gokul Agro Resources": "GOKULAGRO.NS","Goodluck India": "GOODLUCK.NS","Gravita India": "GRAVITA.NS","Happy Forgings": "HAPPYFORGE.NS","HDB Financial Services": "HDBFS.NS","HDFC AMC": "HDFCAMC.NS","Hindustan Aeronautics": "HAL.NS","Hindcon Chemical": "HINDCON.NS","Hindustan Foods": "HNDFDS.NS","Hitachi Energy India": "POWERINDIA.NS","Home First Finance": "HOMEFIRST.NS","India Shelter Finance": "INDIASHLTR.NS","Indian Renewable Energy": "IREDA.NS","Info Edge (India)": "NAUKRI.NS","Insolation Energy": "INA.NS","International Gemmological Institute": "IGI.NS","IOL Chemicals": "IOLCP.NS","JNK India": "JNK.NS","K.P. Energy": "KPEL.NS","Kalyan Jewellers": "KALYANKJIL.NS","KEI Industries": "KEI.NS","Khazanchi Jewellers": "KHAZANCHI.NS","KMC Speciality Hospitals": "KMCSHIL.NS","Krishana Phoschem": "KRISHANA.NS","Krishna Defence": "KRISHNADEF.NS","KRN Heat Exchanger": "KRN.NS","Kwality Pharma": "KWALITY.NS","Landmark Cars": "LANDMARK.NS","Laurus Labs": "LAURUSLABS.NS","Laxmi India Finance": "LAXMIIFIN.NS","Lloyds Metals": "LLOYDSME.NS","M B Agro Products": "MBAPL.NS","Macpower CNC": "MACPOWER.NS","Manorama Industries": "MANORAMA.NS","Marine Electricals": "MARINE.NS","Max Healthcare": "MAXHEALTH.NS","Mazagon Dock Shipbuilders": "MAZDOCK.NS","Minda Corporation": "MINDACORP.NS","Mitsu Chem Plast": "MITSU.NS","Mold-Tek Packaging": "MOLDTKPAC.NS","Monolithisch India": "MONOLITH.NS","MTAR Technologies": "MTARTECH.NS","Multi Commodity Exchange": "MCX.NS","Muthoot Finance": "MUTHOOTFIN.NS","Muthoot Microfin": "MUTHOOTMF.NS","NSDL": "NSDL.NS","Narayana Hrudayalaya": "NH.NS","Navin Fluorine": "NAVINFLUOR.NS","NDR Auto Components": "NDRAUTO.NS","Netweb Technologies": "NETWEB.NS","NINtec Systems": "NINTEC.NS","Nisus Finance": "NISUSFIN.NS","Oberoi Realty": "OBEROIRLTY.NS","OBSC Perfection": "OBSC.NS","P N Gadgil Jewellers": "PNGJL.NS","Paras Defence": "PARAS.NS","Patel Retail": "PATELRETAIL.NS","Persistent Systems": "PERSISTENT.NS","Piccadily Agro": "PICCADIL.NS","Pidilite Industries": "PIDILITIND.NS","Plaza Wires": "PLAZAWIRES.NS","Polycab India": "POLYCAB.NS","Power Mech Projects": "POWERMECH.NS","Precision Wires": "PRECWIRE.NS","Premier Energies": "PREMIERENE.NS","Premier Polyfilm": "PREMIERPOL.NS","Prevest Denpro": "PREVEST.NS","Pricol": "PRICOLLTD.NS","Pritika Engineering": "PRITIKAENG.NS","Privi Speciality Chemicals": "PRIVISCL.NS","Prostarm Info": "PROSTARM.NS","Prudent Corporate Advisory": "PRUDENT.NS","Pyramid Technoplast": "PYRAMID.NS","Quality Power Electrical": "QPOWER.NS","R K Swamy": "RKSWAMY.NS","RR Kabel": "RRKABEL.NS","RACL Geartech": "RACLGEAR.NS","Radhika Jeweltec": "RADHIKAJWE.NS","Raghav Productivity Enhancers": "RAGHAV.NS","Ratnaveer Precision Engineering": "RATNAVEER.NS","RBZ Jewellers": "RBZJEWEL.NS","Redtape": "REDTAPE.NS","Sagility": "SAGILITY.NS","Sai Life Sciences": "SAILIFE.NS","Sakar Healthcare": "SAKAR.NS","Sambhv Steel Tubes": "SAMBHV.NS","Samvardhana Motherson": "MOTHERSON.NS","SBC Exports": "SBC.NS","SBFC Finance": "SBFC.NS","Servotech Renewable Power": "SERVOTECH.NS","SG Finserve": "SGFIN.NS","Shanti Gold": "SHANTIGOLD.NS","Share India Securities": "SHAREINDIA.NS","Shivalik Bimetal Controls": "SBCL.NS","Sigma Solve": "SIGMA.NS","Sirca Paints India": "SIRCA.NS","SJS Enterprises": "SJS.NS","Sky Gold & Diamonds": "SKYGOLD.NS","Solar Industries India": "SOLARINDS.NS","Sona BLW Precision": "SONACOMS.NS","Spectrum Electrical": "SPEC.NS","SRF": "SRF.NS","SRM Contractors": "SRM.NS","Stallion India": "STALLION.NS","Sudeep Pharma": "SUDEEP.NS","Sugs Lloyd": "SUGSLLOYD.NS","Syrma SGS Technology": "SYRMA.NS","TAC Infosec": "TAC.NS","Tatva Chintan Pharma Chem": "TATVA.NS","TBO Tek": "TBOTEK.NS","Tembo Global": "TEMBO.NS","Thangamayil Jewellery": "THANGAMAYL.NS","Tinna Rubber": "TINNARUBR.NS","Titan Biotech": "TITANBIO.NS","Titan Company": "TITAN.NS","Trent": "TRENT.NS","Uniparts India": "UNIPARTS.NS","Uno Minda": "UNOMINDA.NS","V-Marc India": "VMARCIND.NS","Varun Beverages": "VBL.NS","Ventive Hospitality": "VENTIVE.NS","Venus Pipes & Tubes": "VENUSPIPES.NS","Vidya Wires": "VIDYA.NS","Vinati Organics": "VINATIORGA.NS","Vishal Mega Mart": "VMM.NS","Vishnu Chemicals": "VISHNU.NS","Viviana Power": "VIVIANA.NS","Waaree Energies": "WAAREEENER.NS","Waaree Renewables": "WAAREERTL.NS","Yasho Industries": "YASHO.NS","Yatharth Hospital": "YATHARTH.NS","Z-Tech (India)": "ZTECH.NS","Zodiac Energy": "ZODIAC.NS"
}

def load_stocks():
    files = glob.glob("*.xlsx")
    stocks=[]
    for f in files:
        try:
            df=pd.read_excel(f)
            if 'Stock' in df.columns:
                for n in df['Stock'].astype(str):
                    if n in NSE_MAP: stocks.append(NSE_MAP[n])
        except: pass
    if len(stocks)<50: stocks=list(NSE_MAP.values())
    return sorted(list(set(stocks)))

stocks_list=load_stocks()

# TOP BAR - LIKE TRADINGVIEW NIFTY HEADER
top_col1, top_col2 = st.columns([1,4])
with top_col1:
    tf = st.selectbox("", ["Daily","Weekly","Monthly","1 Hour","15 Min"], label_visibility="collapsed")
with top_col2:
    st.caption(f"TRADINGVIEW STYLE | {len(stocks_list)} STOCKS LOADED | {datetime.now().strftime('%d %b %Y %H:%M')} | NSE LIVE")

tf_map={"Daily":("1d","1y"),"Weekly":("1wk","2y"),"Monthly":("1mo","5y"),"1 Hour":("60m","1mo"),"15 Min":("15m","5d")}
interval, default_period = tf_map[tf]

# SIDEBAR - WATCHLIST LIKE IMAGE
st.sidebar.markdown("### Watchlist - Your 227")
period = st.sidebar.selectbox("Period", ["1mo","3mo","6mo","1y","2y"], index=2)
selected = st.sidebar.selectbox("Select Stock (Chart)", stocks_list, index=0)

# MAIN LAYOUT - LEFT CHART RIGHT WATCHLIST
col_chart, col_watch = st.columns([3,1])

@st.cache_data(ttl=300)
def get_data(sym,p,i):
    d=yf.download(sym,period=p,interval=i,auto_adjust=True)
    if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
    return d

def dema(s,l): e1=s.ewm(span=l,adjust=False).mean(); e2=e1.ewm(span=l,adjust=False).mean(); return 2*e1-e2

# RIGHT - WATCHLIST LIVE (Like your image Name Last Chg% Chg)
@st.cache_data(ttl=120)
def get_watchlist_data(symbols):
    data=[]
    for s in symbols[:50]: # First 50 for speed, change to 227 if needed
        try:
            df=yf.download(s,period="2d",interval="1d",progress=False,auto_adjust=True)
            if len(df)>=2:
                last=df['Close'].iloc[-1]; prev=df['Close'].iloc[-2]
                chg=last-prev; chgp=(chg/prev)*100
                data.append({"Name":s.replace(".NS",""),"Last":round(last,2),"Chg":round(chg,2),"Chg%":round(chgp,2)})
        except: pass
    return pd.DataFrame(data)

with col_watch:
    st.markdown("**Name | Last | Chg | Chg%**")
    watch_df = get_watchlist_data(stocks_list)
    if not watch_df.empty:
        # Color coding like TradingView red/green
        def color_chg(val):
            color = 'red' if val < 0 else 'green'
            return f'color: {color}'
        st.dataframe(watch_df.style.applymap(color_chg, subset=['Chg','Chg%']), height=700, use_container_width=True)
    st.caption("Live Watchlist - Like TradingView")

with col_chart:
    df=get_data(selected,period,interval)
    if df.empty: st.error(f"No data {selected}"); st.stop()
    df['DEMA_9']=dema(df['Close'],9); df['DEMA_20']=dema(df['Close'],20); df['DEMA_50']=dema(df['Close'],50); df['DEMA_200']=dema(df['Close'],200)
    support=df.tail(60)['Low'].min(); resistance=df.tail(60)['High'].max()
    last=df.iloc[-1]; prev=df.iloc[-2]
    chg=last['Close']-prev['Close']; chgp=(chg/prev['Close'])*100

    # HEADER LIKE YOUR IMAGE: Nifty 50 23,329.00 -0.43%
    c1,c2,c3 = st.columns([1,1,2])
    c1.markdown(f"### {selected.replace('.NS','')} **{last['Close']:.2f}**")
    c2.markdown(f"<span style='color:{'green' if chg>=0 else 'red'}'> {chg:.2f} {chgp:.2f}% </span>", unsafe_allow_html=True)
    c3.markdown(f"**Support:** {support:.2f} | **Resistance:** {resistance:.2f} | **DEMA9:** {last['DEMA_9']:.2f} | **DEMAND/SUPPLY ACTIVE**")

    fig=go.Figure()
    # TradingView style area chart + candles
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', line=dict(color='#ef5350', width=1.5), name="Price", fillcolor='rgba(239,83,80,0.2)'))
    fig.add_trace(go.Candlestick(x=df.index,open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'],name="OHLC", opacity=0.8))
    fig.add_trace(go.Scatter(x=df.index,y=df['DEMA_9'],line=dict(color="yellow",width=2),name="DEMA9"))
    fig.add_trace(go.Scatter(x=df.index,y=df['DEMA_20'],line=dict(color="orange",width=1),name="DEMA20"))
    fig.add_trace(go.Scatter(x=df.index,y=df['DEMA_50'],line=dict(color="#2962ff",width=1),name="DEMA50"))
    fig.add_trace(go.Scatter(x=df.index,y=df['DEMA_200'],line=dict(color="white",width=1),name="DEMA200"))
    fig.add_hline(y=support, line_dash="dash", line_color="lime", annotation_text=f"Demand/Support {support:.2f}")
    fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text=f"Supply/Resistance {resistance:.2f}")
    fig.add_hrect(y0=support, y1=support*1.03, fillcolor="green", opacity=0.1)
    fig.add_hrect(y0=resistance*0.97, y1=resistance, fillcolor="red", opacity=0.1)
    fig.update_layout(template="plotly_dark", height=650, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

    sig="BUY ✅" if last['Close']>last['DEMA_9'] else "SELL ❌"
    st.markdown(f"**Signal: {sig} | Close above DEMA9?** {'YES' if last['Close']>last['DEMA_9'] else 'NO'} | **Volume:** {last['Volume']:,}")
