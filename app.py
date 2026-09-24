import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(page_title="NSE 227 - Demand Supply + SR + Signals", layout="wide")
st.title("NSE 227 Dashboard - YOUR Stocks | Demand-Supply BOX + S/R + BUY/SELL")

# ---------- LOAD YOUR 227 STOCKS ----------
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
st.success(f"Loaded {len(companies)} stocks from YOUR Excel" if len(companies)==227 else f"Loaded {len(companies)} stocks")

# ---------- TICKER MAP (Full 227) ----------
TICKER_MAP = {
"Aadhar Hsg. Fin.": "AADHARHFC", "Aarti Industries": "AARTIIND", "Aarti Surfactant": "AARTISURF",
"Aarvi Encon": "AARVI", "AAVAS Financiers": "AAVAS", "Acutaas Chemical": "ACUTAAS",
"ADF Foods": "ADFFOODS", "Aditya Infotech": "ADITYA", "Aditya Vision": "ADITYAVISION",
"Advait Energy": "ADVAIT", "Aeroflex": "AEROFLEX", "Aether Industries": "AETHER",
"Afcom Holdings": "AFCOM", "Affle 3i": "AFFLE", "AGI Infra": "AGI", "Ajanta Pharma": "AJANTPHARM",
"Alpex Solar": "ALPEXSOLAR", "Anand Rathi Share": "ANANDRATHI", "Anand Rathi Wealth": "ANANDRATHI",
"Anant Raj": "ANANTRAJ", "Anlon Healthcare": "ANLON", "Anupam Rasayan": "ANURAS",
"Apar Industries": "APARINDS", "APL Apollo Tubes": "APLAPOLLO", "Apollo Hospitals": "APOLLOHOSP",
"Apollo Micro Systems": "APOLLO", "Aptus Value Housing": "APTUS", "Arman Financial": "ARMANFIN",
"Artemis Medicare": "ARTEMISMED", "Asarfi Hospital": "ASARFI", "Asian Paints": "ASIANPAINT",
"ASK Automotive": "ASK", "ASM Technologies": "ASMTEC", "Astral": "ASTRAL", "Atlanta Electric": "ATLANT",
"Avalon Technologies": "AVALON", "Avenue Supermarts": "DMART", "Borana Weaves": "BORANA",
"Britannia Industries": "BRITANNIA", "BSE": "BSE", "Campus Activewear": "CAMPUS",
"Can Fin Homes": "CANFINHOME", "CarTrade Tech": "CARTRADE", "Ceinsys Tech": "CEINSYSTECH",
"Cellecor Gadgets": "CELLECOR", "CFF Fluid Control": "CFF", "CG Power & Indl": "CGPOWER",
"Chandan Healthcare": "CHANDAN", "Choice International": "CHOICEIN", "Craftsman Automation": "CRAFTSMAN",
"CRISIL": "CRISIL", "Cupid": "CUPID", "D.P. Abhushan": "DPABHUSHAN", "Data Pattern": "DATAPATTNS",
"DEE Development Engineers": "DEEDEV", "Deep Industries": "DEEPINDS", "Delton Cables": "DELTON",
"Divgi TorqTransfer": "DIVGIITTS", "DRC Systems": "DRCSYSTEMS", "Dynamic Cables": "DYNAMIC",
"Eicher Motors": "EICHERMOT", "Emmvee Photovoltaic": "EMMVEE", "eMudhra": "EMUDHRA",
"Entero Healthcare": "ENTERO", "EPACK Prefab": "EPACK", "Ethos": "ETHOSLTD",
"Finolex Cables": "FINCABLES", "Gala Precision": "GALAPREC", "Gandhar Oil Refinery": "GANDHAR",
"Garden Reach Shipbuilders": "GRSE", "Gland Pharma": "GLAND", "Global Health": "MEDANTA",
"Gravita India": "GRAVITA", "Happy Forgings": "HAPPYFORGE", "HDFC AMC": "HDFCAMC",
"Hindustan Aeronautics": "HAL", "Hitachi Energy": "POWERINDIA", "Home First Finance": "HOMEFIRST",
"India Shelter Finance": "INDIASHLTR", "Indian Renewable Energy": "IREDA", "Info Edge": "NAUKRI",
"IOL Chemicals": "IOLCP", "Kalyan Jewellers": "KALYANKJIL", "KEI Industries": "KEI",
"Laurus Labs": "LAURUSLABS", "Max Healthcare": "MAXHEALTH", "Mazagon Dock": "MAZDOCK",
"Muthoot Finance": "MUTHOOTFIN", "NSDL": "NSDL", "Narayana Hrudayalaya": "NH",
"Navin Fluorine": "NAVINFLUOR", "Netweb Technologies": "NETWEB", "Oberoi Realty": "OBEROIRLTY",
"Paras Defence": "PARAS", "Persistent Systems": "PERSISTENT", "Pidilite Industries": "PIDILITIND",
"Polycab India": "POLYCAB", "Power Mech Projects": "POWERMECH", "Premier Energies": "PREMIERENE",
"RR Kabel": "RRKABEL", "SRF": "SRF", "Solar Industries": "SOLARINDS", "Sona BLW Precision": "SONACOMS",
"TBO Tek": "TBOTEK", "Titan Company": "TITAN", "Trent": "TRENT", "Uno Minda": "UNOMINDA",
"Varun Beverages": "VBL", "Vinati Organics": "VINATIORGA", "Waaree Energies": "WAAREEENER",
"Waaree Renewable": "WAAREERTL", "Zodiac Energy": "ZODIAC", "Titan Biotech": "TITANBIO",
"Thangamayil Jewellery": "THANGAMAYL", "Vishal Mega Mart": "VMM", "Vishnu Chemicals": "VISHNU",
"Redtape": "REDTAPE", "Sagility": "SAGILITY", "Sai Life Sciences": "SAILIFE"
}

def get_ticker(c):
    return TICKER_MAP.get(c.strip(), c.upper().replace(" ","").replace(".","").replace("&","")[:10])

tickers = [get_ticker(c) for c in companies]
yf_tickers = [f"{t}.NS" for t in tickers]

# ---------- INDICATORS ----------
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1+rs))

def calc_levels(df):
    # df has Close, High, Low, Volume
    if len(df) < 20:
        return None
    close = df['Close']
    high = df['High']; low = df['Low']
    # Support = 20-day low, Resistance = 20-day high
    support = float(low.tail(20).min())
    resistance = float(high.tail(20).max())
    # Demand Zone = Support +- 3%, Supply = Resistance +-3%
    demand_low = round(support*0.97,2); demand_high = round(support*1.03,2)
    supply_low = round(resistance*0.97,2); supply_high = round(resistance*1.03,2)
    # RSI
    r = float(rsi(close).iloc[-1]) if len(close)>14 else 50
    # MA
    ma20 = float(close.tail(20).mean()); ma50 = float(close.tail(50).mean()) if len(close)>=50 else ma20
    last = float(close.iloc[-1])
    # BUY/SELL Logic
    signal = "HOLD"; strength = ""
    # BUY: price near demand zone + RSI <45 + above MA20 or bounce
    if last <= demand_high*1.02 and r < 48:
        signal = "BUY"; strength = "Strong Demand"
    elif last <= demand_high*1.05 and r < 55 and last > ma20:
        signal = "BUY"; strength = "Demand Bounce"
    # SELL: near supply + RSI >52
    elif last >= supply_low*0.98 and r > 52:
        signal = "SELL"; strength = "Strong Supply"
    elif last >= supply_low*0.95 and r > 65:
        signal = "SELL"; strength = "Supply Overbought"
    # Trend
    if ma20 > ma50 and signal=="BUY": strength += " + Uptrend"
    if ma20 < ma50 and signal=="SELL": strength += " + Downtrend"

    return {
        "Support": support, "Resistance": resistance,
        "Demand Zone": f"{demand_low}-{demand_high}",
        "Supply Zone": f"{supply_low}-{supply_high}",
        "Demand Low": demand_low, "Demand High": demand_high,
        "Supply Low": supply_low, "Supply High": supply_high,
        "RSI": round(r,1), "MA20": round(ma20,1), "Last": round(last,2),
        "Signal": signal, "Strength": strength
    }

# ---------- FETCH LIVE + CALC ----------
@st.cache_data(ttl=900)
def fetch_all(yf_tickers, companies):
    # Batch download 3 months for S/R
    try:
        data = yf.download(yf_tickers, period="3mo", interval="1d", group_by='ticker', threads=True, progress=False, auto_adjust=True)
    except Exception as e:
        st.error(f"Yahoo error {e}"); return pd.DataFrame()

    rows=[]
    for comp, t, yft in zip(companies, tickers, yf_tickers):
        try:
            if len(yf_tickers)==1:
                df = data
            else:
                if yft not in data.columns.levels[0]: continue
                df = data[yft]
            df = df.dropna()
            if len(df) < 20: continue
            levels = calc_levels(df)
            if not levels: continue
            # Distance from zones
            last = levels['Last']
            dist_sup = round(((levels['Resistance']-last)/last*100),2)
            dist_dem = round(((last-levels['Support'])/last*100),2)

            rows.append({
                "S.No": companies.index(comp)+1,
                "Stock": comp,
                "Ticker": t,
                "CMP": last,
                "Support": levels['Support'],
                "Resistance": levels['Resistance'],
                "Demand Zone BOX": levels['Demand Zone'],
                "Supply Zone BOX": levels['Supply Zone'],
                "RSI": levels['RSI'],
                "Dist to Support %": dist_dem,
                "Dist to Resistance %": dist_sup,
                "Signal": levels['Signal'],
                "Setup": levels['Strength']
            })
        except:
            continue
    return pd.DataFrame(rows)

with st.spinner("Fetching LIVE + Calculating Demand-Supply + S/R + Signals for YOUR 227... (30 sec)"):
    live_df = fetch_all(yf_tickers, companies)

if live_df.empty:
    st.warning("Yahoo blocked or ticker mismatch. Showing Excel data.")
    st.dataframe(master_df)
else:
    # Filters
    c1,c2,c3 = st.columns(3)
    with c1: sig_filter = st.selectbox("Filter Signal", ["ALL","BUY","SELL","HOLD"])
    with c2: rsi_filter = st.slider("RSI Max for BUY", 30,70,55)
    with c3: search = st.text_input("Search Stock")

    filtered = live_df.copy()
    if sig_filter!="ALL": filtered = filtered[filtered['Signal']==sig_filter]
    if sig_filter=="BUY": filtered = filtered[filtered['RSI']<=rsi_filter]
    if search: filtered = filtered[filtered['Stock'].str.contains(search, case=False)]

    # Color
    def color_sig(val):
        if val=="BUY": return "background-color: #0a5c36; color: white"
        if val=="SELL": return "background-color: #7a1a1a; color: white"
        return ""

    st.dataframe(filtered.style.applymap(color_sig, subset=['Signal']), use_container_width=True, height=600)

    # Summary boxes
    buys = len(live_df[live_df['Signal']=="BUY"]); sells = len(live_df[live_df['Signal']=="SELL"])
    st.metric("BUY Signals (Near Demand)", buys); st.metric("SELL Signals (Near Supply)", sells)

    st.download_button("Download FULL 227 with S/R + Zones + Signals CSV", live_df.to_csv(index=False), "NSE_227_Demand_Supply_SR_Signals.csv")

    # Show detail for selected stock
    st.subheader("Demand-Supply BOX Detail")
    sel = st.selectbox("Select Stock for BOX view", live_df['Stock'].tolist())
    row = live_df[live_df['Stock']==sel].iloc[0]
    st.code(f"""
Stock: {row['Stock']} ({row['Ticker']})
CMP: {row['CMP']}

SUPPORT: {row['Support']} -> DEMAND BOX: {row['Demand Zone BOX']} [BUY ZONE]
RESISTANCE: {row['Resistance']} -> SUPPLY BOX: {row['Supply Zone BOX']} [SELL ZONE]
RSI: {row['RSI']}
Signal: {row['Signal']} - {row['Setup']}

BUY when price enters Demand BOX (Support zone)
SELL when price enters Supply BOX (Resistance zone)
""")
