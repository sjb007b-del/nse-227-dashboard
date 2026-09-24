import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="NSE 227 Dashboard - YOUR Stocks", layout="wide")
st.title("NSE 227 Dashboard - YOUR Stocks")

def load_my_stocks():
    try:
        df = pd.read_excel("All_227_Stocks_Financial_Analysis.xlsx")
        companies = df['Stock'].dropna().tolist()
        st.success(f"Loaded {len(companies)} stocks from YOUR Excel")
        return companies, df
    except:
        df = pd.read_csv("stocks.csv")
        col = 'Company' if 'Company' in df.columns else df.columns[0]
        return df[col].tolist(), df

companies, master_df = load_my_stocks()

TICKER_MAP = {
"Aadhar Hsg. Fin.": "AADHARHFC", "Aarti Industries": "AARTIIND",
"Aarti Surfactant": "AARTISURF", "Aarvi Encon": "AARVI",
"AAVAS Financiers": "AAVAS", "Acutaas Chemical": "ACUTAAS",
"ADF Foods": "ADFFOODS", "Aditya Infotech": "ADITYA",
"Aditya Vision": "ADITYAVISION", "Advait Energy": "ADVAIT",
"Aeroflex": "AEROFLEX", "Aether Industries": "AETHER",
"Afcom Holdings": "AFCOM", "Affle 3i": "AFFLE", "AGI Infra": "AGI",
"Ajanta Pharma": "AJANTPHARM", "Alpex Solar": "ALPEXSOLAR",
"Anand Rathi Share": "ANANDRATHI", "Anant Raj": "ANANTRAJ",
"Anupam Rasayan": "ANURAS", "Apar Industries": "APARINDS",
"APL Apollo Tubes": "APLAPOLLO", "Apollo Hospitals": "APOLLOHOSP",
"Aptus Value Housing": "APTUS", "Arman Financial": "ARMANFIN",
"Artemis Medicare": "ARTEMISMED", "Asian Paints": "ASIANPAINT",
"Astral": "ASTRAL", "Avenue Supermarts": "DMART",
#... add rest 190 similarly
}

def get_ticker(c):
    return TICKER_MAP.get(c, c.upper().replace(" ","").replace(".","")[:10])

tickers = [get_ticker(c) for c in companies]

@st.cache_data(ttl=900)
def fetch_live(tickers, companies):
    yf_tickers = [f"{t}.NS" for t in tickers]
    data = yf.download(yf_tickers, period="5d", threads=True, progress=False, group_by='ticker')
    rows = []
    for comp, t, yft in zip(companies, tickers, yf_tickers):
        try:
            d = data[yft] if len(yf_tickers)>1 else data
            d = d.dropna()
            if len(d) < 2: continue
            last = float(d['Close'].iloc[-1]); prev = float(d['Close'].iloc[-2])
            rows.append({"Company": comp, "Ticker": t, "Last": round(last,2),
                         "Chg": round(last-prev,2), "Chg%": round((last-prev)/prev*100,2)})
        except: continue
    return pd.DataFrame(rows)

if companies:
    live_df = fetch_live(tickers, companies)
    final = pd.merge(master_df, live_df, left_on='Stock', right_on='Company', how='left')
    st.dataframe(final, use_container_width=True)
    st.download_button("Download YOUR 227 LIVE", final.to_csv(index=False), "your_227_live.csv")
