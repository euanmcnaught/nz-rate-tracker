import pandas as pd
import requests
import io
import os

print("Starting Bridge Script...")

url = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    print("Downloading file...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    print("Loading Excel...")
    df_full = pd.read_excel(io.BytesIO(response.content), sheet_name="Data", header=None)
    
    print("Searching for Series IDs...")
    series_ids = df_full.iloc[4, :].astype(str)
    
    # Locate indices
    idx_ocr = series_ids[series_ids.str.contains('INM.DP1.N', na=False)].index[0]
    print(f"OCR Index found: {idx_ocr}")
    
    # ... (rest of your logic)
    print("Successfully processed data.")

except Exception as e:
    print(f"FAILED: {e}")
    exit(1) # This forces the code to give you the exit code 1 to show the log
