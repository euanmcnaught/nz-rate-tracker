import streamlit as st
import pandas as pd
from urllib.request import Request, urlopen

@st.cache_data(ttl=14400)
def fetch_official_rbnz_rates():
    url = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"
    
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as response:
        # 1. Load the raw data, preserving all rows
        df_full = pd.read_excel(response, sheet_name="Data", header=None)
    
    # 2. Extract the Series ID row (Row 5 in Excel is index 4 in pandas)
    series_ids = df_full.iloc[4, :].astype(str)
    
    # 3. Locate columns using your specific IDs
    # OCR: INM.DP1.N | 90-Day: INM.DB03.NZZV | 10-Year: INM.DG110.NZZCF
    # Note: Search for partial matches to account for potential formatting changes
    try:
        idx_date = 0
        idx_ocr = series_ids[series_ids.str.contains('INM.DP1.N', na=False)].index[0]
        idx_90d = series_ids[series_ids.str.contains('INM.DB03.NZZV', na=False)].index[0]
        idx_10y = series_ids[series_ids.str.contains('INM.DG110.NZZCF', na=False)].index[0]
    except IndexError:
        raise ValueError("Could not locate required Series IDs in the RBNZ spreadsheet.")

    # 4. Slice and clean
    df = df_full.iloc[5:, [idx_date, idx_ocr, idx_90d, idx_10y]].copy()
    df.columns = ['Date', 'OCR', '90-Day Bill', '10-Year Bond']
    
    # 5. Data cleaning
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    for col in ['OCR', '90-Day Bill', '10-Year Bond']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df.dropna(subset=['Date']).sort_values('Date').reset_index(drop=True)
