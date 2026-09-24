@st.cache_data(ttl=900)
def fetch_all(yf_tickers, companies):
    rows=[]
    for i in range(0, len(yf_tickers), 30):
        batch_ns = yf_tickers[i:i+30]
        batch_bo = [t.replace(".NS",".BO") for t in batch_ns]
        batch_comps = companies[i:i+30]
        batch_tickers = tickers[i:i+30]
        try:
            # Try NSE first
            data_ns = yf.download(batch_ns, period="3mo", group_by='ticker', threads=False, progress=False, auto_adjust=True)
            # Try BSE for failed ones
            data_bo = yf.download(batch_bo, period="3mo", group_by='ticker', threads=False, progress=False, auto_adjust=True)

            for comp, t, yft_ns, yft_bo in zip(batch_comps, batch_tickers, batch_ns, batch_bo):
                df=None
                try:
                    if len(batch_ns)==1:
                        df=data_ns if not data_ns.empty else data_bo
                    else:
                        if yft_ns in data_ns.columns.levels[0] and not data_ns[yft_ns].dropna().empty:
                            df=data_ns[yft_ns]
                        elif yft_bo in data_bo.columns.levels[0]:
                            df=data_bo[yft_bo]
                    if df is None or len(df.dropna())<20: continue
                    df=df.dropna()
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
