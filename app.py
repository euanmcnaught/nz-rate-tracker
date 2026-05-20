@st.cache_data(ttl=14400)
def fetch_official_rbnz_rates():
    url = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"
    
    # Use a real user agent to bypass the RBNZ firewall
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    req = Request(url, headers=headers)
    
    try:
        with urlopen(req) as response:
            # Explicitly force engine='openpyxl' and use the binary stream
            df_full = pd.read_excel(response, sheet_name="Data", header=None, engine='openpyxl')
        
        # Log to your terminal/console to verify what's happening
        print("Data successfully loaded. Extracting Series IDs...")
        
        series_ids = df_full.iloc[4, :].astype(str)
        
        # Locate indices
        idx_date = 0
        idx_ocr = series_ids[series_ids.str.contains('INM.DP1.N', na=False)].index[0]
        idx_90d = series_ids[series_ids.str.contains('INM.DB03.NZZV', na=False)].index[0]
        idx_10y = series_ids[series_ids.str.contains('INM.DG110.NZZCF', na=False)].index[0]

        df = df_full.iloc[5:, [idx_date, idx_ocr, idx_90d, idx_10y]].copy()
        df.columns = ['Date', 'OCR', '90-Day Bill', '10-Year Bond']
        
        # Cleanup
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        for col in ['OCR', '90-Day Bill', '10-Year Bond']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df.dropna(subset=['Date']).sort_values('Date').reset_index(drop=True)

    except Exception as e:
        # This error message will appear in your Streamlit app interface if it fails
        st.error(f"Failed to load RBNZ data: {str(e)}")
        return pd.DataFrame() # Return empty to stop the app from hanging
