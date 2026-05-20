import pandas as pd
import requests
import io

def create_clean_data():
    url = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    df_full = pd.read_excel(io.BytesIO(response.content), sheet_name="Data", header=None)
    series_ids = df_full.iloc[4, :].astype(str)
    
    idx_date = 0
    idx_ocr = series_ids[series_ids.str.contains('INM.DP1.N', na=False)].index[0]
    idx_90d = series_ids[series_ids.str.contains('INM.DB03.NZZV', na=False)].index[0]
    idx_10y = series_ids[series_ids.str.contains('INM.DG110.NZZCF', na=False)].index[0]

    df = df_full.iloc[5:, [idx_date, idx_ocr, idx_90d, idx_10y]].copy()
    df.columns = ['Date', 'OCR', '90-Day Bill', '10-Year Bond']
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    for col in ['OCR', '90-Day Bill', '10-Year Bond']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['Date']).sort_values('Date')
    df.to_csv('rates_data.csv', index=False)

if __name__ == "__main__":
    create_clean_data()
