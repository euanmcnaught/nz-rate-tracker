import streamlit as st
import pandas as pd
from urllib.request import Request, urlopen

# Set up the dashboard page
st.set_page_config(page_title="RBNZ Rates Monitor", layout="wide")
st.title("🇳🇿 Official RBNZ Data Monitor")

@st.cache_data(ttl=14400)
def fetch_official_rbnz_rates():
    url = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = Request(url, headers=headers)
    
    try:
        # Load raw Excel; header=None allows us to handle the specific Row 5 Series IDs
        with urlopen(req) as response:
            df_full = pd.read_excel(response, sheet_name="Data", header=None, engine='openpyxl')
        
        # Row 5 (index 4) contains the Series IDs
        series_ids = df_full.iloc[4, :].astype(str)
        
        # Locate columns by Series ID
        # OCR: INM.DP1.N | 90-Day: INM.DB03.NZZV | 10-Year: INM.DG110.NZZCF
        idx_date = 0
        idx_ocr = series_ids[series_ids.str.contains('INM.DP1.N', na=False)].index[0]
        idx_90d = series_ids[series_ids.str.contains('INM.DB03.NZZV', na=False)].index[0]
        idx_10y = series_ids[series_ids.str.contains('INM.DG110.NZZCF', na=False)].index[0]

        # Slice data starting from Row 6 (index 5)
        df = df_full.iloc[5:, [idx_date, idx_ocr, idx_90d, idx_10y]].copy()
        df.columns = ['Date', 'OCR', '90-Day Bill', '10-Year Bond']
        
        # Convert types
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        for col in ['OCR', '90-Day Bill', '10-Year Bond']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df.dropna(subset=['Date']).sort_values('Date').reset_index(drop=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Run the fetch and display
df = fetch_official_rbnz_rates()

if not df.empty:
    st.success("Data successfully synchronized from RBNZ.")
    st.write("Latest Data Points:")
    st.dataframe(df.tail())
    
    st.subheader("Historical Trends")
    st.line_chart(df.set_index('Date')[['OCR', '90-Day Bill', '10-Year Bond']])
else:
    st.warning("No data found. Please check network connection.")
