@st.cache_data(ttl=14400)
def fetch_official_rbnz_rates():
    url = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"
    
    # Advanced browser headers to bypass 403 Forbidden firewall blocks
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    
    req = Request(url, headers=headers)
    
    try:
        with urlopen(req) as response:
            # We load the binary content into a buffer for pandas
            df_full = pd.read_excel(response.read(), sheet_name="Data", header=None, engine='openpyxl')
        
        # [Keep the rest of your Series ID logic the same as the previous block]
        series_ids = df_full.iloc[4, :].astype(str)
        # ... (rest of your logic)
