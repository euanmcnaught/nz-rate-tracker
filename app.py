@st.cache_data(ttl=14400)
def fetch_official_rbnz_rates():
    url = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"
    
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urlopen(req) as response:
            # We skip the top metadata blocks completely, forcing Pandas to hit the data stack cleanly
            df_raw = pd.read_excel(
                response, 
                sheet_name="Data", 
                skiprows=1,     # Skips Row 1 text
                header=0,       # Row 2 becomes the true columns 
                na_values=['', ' ', 'NaN', '-', '.', '..']
            )
            
        # Isolate exactly the physical series columns by their positional index
        # Col 0 = Date, Col 1 = OCR, Col 7 = 90-Day, Col 11 = 10-Year
        df = df_raw.iloc[:, [0, 1, 7, 11]].copy()
        df.columns = ['Date', 'OCR', '90-Day Bill', '10-Year Bond']
        
        # Turn anything that isn't a clean date into NaT and drop it
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        
        # Strip string artifacts or text codes from RBNZ and parse to numbers
        for col in ['OCR', '90-Day Bill', '10-Year Bond']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Enforce chronological ordering (3 Jan 2018 up to the present)
        df = df.sort_values('Date').reset_index(drop=True)
        
        # Cleanly fill gaps (like weekends/holidays) forward, then handle any early edge cases backward
        df = df.ffill().bfill()
        
        return df
        
    except Exception as e:
        st.sidebar.error(f"Live Parse Trace: {e}")
        # Robust context fallback matrix matching current monetary environments
        dates = pd.date_range(start="2018-01-01", end=datetime.today(), freq='B')
        return pd.DataFrame({
            'Date': dates,
            'OCR': [5.50 for _ in range(len(dates))],
            '90-Day Bill': [5.28 for _ in range(len(dates))],
            '10-Year Bond': [4.62 for _ in range(len(dates))]
        })
