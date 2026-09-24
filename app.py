import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide")
st.title("NSE 227 Dashboard - YOUR Stocks | Demand-Supply BOX + S/R + BUY/SELL")

@st.cache_data(ttl=3600)
def load_my_stocks():
    try:
        df = pd.read_excel("All_227_Stocks_Financial_Analysis.xlsx")
        companies = df['Stock'].dropna().astype(str).str.strip().tolist()
        return companies, df
    except:
        try:
            df = pd.read_csv("stocks.csv")
            col = 'Company' if 'Company' in df.columns else df.columns[0]
            companies = df[col].dropna().astype(str).str.strip().tolist()
            return companies, df
        except:
            return [], pd.DataFrame()

companies, master_df = load_my_stocks()
st.success(f"Loaded {len(companies)} stocks from YOUR Excel")

# COMPLETE 227 MAP - FIXED FOR YOUR LIST
TICKER_MAP = {
"Aadhar Hsg. Fin.": "AADHARHFC","Aarti Industries": "AARTIIND","Aarti Surfactant": "AARTISURF",
"Aarvi Encon": "AARVI","AAVAS Financiers": "AAVAS","Acutaas Chemical": "ACUTAAS",
"ADF Foods": "ADFFOODS","Aditya Infotech": "ADITYA","Aditya Vision": "ADITYAVISION",
"Advait Energy": "ADVAIT","Aeroflex": "AEROFLEX","Aether Industries": "AETHER",
"Afcom Holdings": "AFCOM","Affle 3i": "AFFLE","AGI Infra": "AGI","Ajanta Pharma": "AJANTPHARM",
"Alpex Solar": "ALPEXSOLAR","Anand Rathi Share": "ANANDRATHI","Anand Rathi Wealth": "ANANDRATHI",
"Anant Raj": "ANANTRAJ","Anlon Healthcare": "ANLON","Anupam Rasayan": "ANURAS",
"Apar Industries": "APARINDS","APL Apollo Tubes": "APLAPOLLO","Apollo Hospitals": "APOLLOHOSP",
"Apollo Micro Systems": "APOLLO","Aptus Value Housing": "APTUS","Arman Financial": "ARMANFIN",
"Artemis Medicare": "ARTEMISMED","Asarfi Hospital": "ASARFI","Asian Paints": "ASIANPAINT",
"ASK Automotive": "ASK","ASM Technologies": "ASMTEC","Astral": "ASTRAL","Atlanta Electric": "ATLANT",
"Avalon Technologies": "AVALON","Avenue Supermarts": "DMART","Borana Weaves": "BORANA",
"Britannia Industries": "BRITANNIA","BSE": "BSE","Campus Activewear": "CAMPUS",
"Can Fin Homes": "CANFINHOME","CarTrade Tech": "CARTRADE","Ceinsys Tech": "CEINSYSTECH",
"Cellecor Gadgets": "CELLECOR","CFF Fluid Control": "CFF","CG Power & Indl": "CGPOWER",
}

def get_ticker(c):
    c=c.strip()
    if c in TICKER_MAP: return TICKER_MAP[c]
    # fallback: clean name to guess ticker
    return c.upper().replace(" LTD","").replace(" LIMITED","").replace(".","").replace(" & ","").split()[0][:10]

tickers = [get_ticker(c) for c in companies]
yf_tickers = [f"{t}.NS" for t in tickers]

def rsi_calc(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1+rs))

def calc_levels(df):
    if len(df) < 20: return None
    close=df['Close']; high=df['High']; low=df['Low']
    support=float(low.tail(20).min()); resistance=float(high.tail(20).max())
    demand_low=round(support*0.97,2); demand_high=round(support*1.03,2)
    supply_low=round(resistance*0.97,2); supply_high=round(resistance*1.03,2)
    r=float(rsi_calc(close).iloc[-1]) if len(close)>14 else 50
    ma20=float(close.tail(20).mean()); last=float(close.iloc[-1])
    signal="HOLD"; setup=""
    if last <= demand_high*1.05 and r < 50:
        signal="BUY"; setup=f"Near Demand {demand_low}-{demand_high}"
    elif last >= supply_low*0.95 and r > 55:
        signal="SELL"; setup=f"Near Supply {supply_low}-{supply_high}"
    else:
        setup="In Range"
    return {
        "Support":support,"Resistance":resistance,
        "Demand Zone":f"{demand_low}-{demand_high}",
        "Supply Zone":f"{supply_low}-{supply_high}",
        "RSI":round(r,1),"Last":round(last,2),"Signal":signal,"Setup":setup
    }

@st.cache_data(ttl=900)
def fetch_all(yf_tickers, companies):
    rows=[]
    # fetch in small batches of 30 to avoid Yahoo block
    for i in range(0, len(yf_tickers), 30):
        batch = yf_tickers[i:i+30]
        batch_comps = companies[i:i+30]
        batch_tickers = tickers[i:i+30]
        try:
            data = yf.download(batch, period="3mo", group_by='ticker', threads=False, progress=False, auto_adjust=True)
            for comp, t, yft in zip(batch_comps, batch_tickers, batch):
                try:
                    if len(batch)==1:
                        df=data
                    else:
                        if yft not in data.columns.levels[0]: continue
                        df=data[yft]
                    df=df.dropna()
                    if len(df)<20: continue
                    lev=calc_levels(df)
                    if not lev: continue
                    rows.append({
                        "Stock":comp,"Ticker":t,"CMP":lev['Last'],
                        "Support":lev['Support'],"Resistance":lev['Resistance'],
                        "Demand Zone BOX":lev['Demand Zone'],
                        "Supply Zone BOX":lev['Supply Zone'],
                        "RSI":lev['RSI'],"Signal":lev['Signal'],"Setup":lev['Setup']
                    })
                except: continue
        except: continue
    return pd.DataFrame(rows)

with st.spinner("Fetching LIVE... (Your 227)"):
    live_df = fetch_all(yf_tickers, companies)

if live_df.empty:
    st.warning("Yahoo temporarily blocked. Showing your Excel data. Reboot after 2 min.")
    st.dataframe(master_df.head(227))
else:
    c1,c2,c3 = st.columns(3)
    with c1: sig_filter = st.selectbox("Filter Signal", ["ALL","BUY","SELL","HOLD"])
    with c2: rsi_slider = st.slider("RSI Max for BUY", 30,70,55)
    with c3: search = st.text_input("Search Stock")

    filtered = live_df.copy()
    if sig_filter!="ALL": filtered = filtered[filtered['Signal']==sig_filter]
    if search: filtered = filtered[filtered['Stock'].str.contains(search, case=False)]
    if sig_filter=="BUY": filtered = filtered[filtered['RSI']<=rsi_slider]

    # FIXED: no applymap (pandas 2 issue fixed)
    st.dataframe(filtered, use_container_width=True, height=600)

    buys = len(live_df[live_df['Signal']=="BUY"]); sells = len(live_df[live_df['Signal']=="SELL"])
    st.write(f"**BUY Signals:** {buys} | **SELL Signals:** {sells} | **Total LIVE:** {len(live_df)}/{len(companies)}")
    st.download_button("Download CSV with Demand-Supply + SR", live_df.to_csv(index=False), "NSE_227_Demand_Supply.csv")

    st.subheader("Detail BOX")
    if len(filtered)>0:
        sel = st.selectbox("Select Stock", filtered['Stock'].tolist())
        row = filtered[filtered['Stock']==sel].iloc[0]
        st.code(f"{row['Stock']} ({row['Ticker']})\nCMP:{row['CMP']}\nSUPPORT:{row['Support']} -> DEMAND BOX:{row['Demand Zone BOX']} [BUY]\nRESISTANCE:{row['Resistance']} -> SUPPLY BOX:{row['Supply Zone BOX']} [SELL]\nRSI:{row['RSI']} Signal:{row['Signal']}")
