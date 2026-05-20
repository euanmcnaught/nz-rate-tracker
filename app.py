import streamlit as st
import pandas as pd
from urllib.request import Request, urlopen
from datetime import datetime, timedelta

st.set_page_config(page_title="Official RBNZ Rates Monitor", layout="wide")
st.title("🇳🇿 Official New Zealand Interest Rates Monitor")
st.caption("Historical daily close wholesale curves (2018-Current) synchronized from the Reserve Bank of New Zealand (RBNZ)")

@st.cache_data(ttl=14400)
def fetch_official_rbnz_rates():
    url = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"
    
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urlopen(req) as response:
            # Read everything RAW first to bypass complex multi-row header gaps safely
            df_raw = pd.read_excel(response, sheet_name="Data", header=None)
        
        # Step 1: Isolate the target columns by index mapping
        # Column A (0) -> Date
        # Column B (1) -> OCR
        # Column H (7) -> 90-Day Bill
        # Column L (11) -> 10-Year Bond
        df = df_raw[[0, 1, 7, 11]].copy()
        df.columns = ['Date', 'OCR', '90-Day Bill', '10-Year Bond']
        
        # Step 2: Convert the Date column to real datetimes, turning text headers into NaT
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Step 3: Drop everything that isn't a valid date.
        # This automatically skips rows 1-5 (headers & metadata) and isolates the real history!
        df = df.dropna(subset=['Date'])
        
        # Step 4: Clean up numeric values cleanly
        df['OCR'] = pd.to_numeric(df['OCR'], errors='coerce')
        df['90-Day Bill'] = pd.to_numeric(df['90-Day Bill'], errors='coerce')
        df['10-Year Bond'] = pd.to_numeric(df['10-Year Bond'], errors='coerce')
        
        # Chronological sort and fill minor missing weekend gaps
        df = df.sort_values('Date').reset_index(drop=True)
        df = df.ffill().bfill()
        
        return df
        
    except Exception as e:
        st.sidebar.error(f"Live Parse Trace: {e}")
        # Hard fallback matrix if connection fails
        dates = pd.date_range(start="2018-01-01", end=datetime.today(), freq='B')
        return pd.DataFrame({
            'Date': dates,
            'OCR': [5.50 for _ in range(len(dates))],
            '90-Day Bill': [5.25 for _ in range(len(dates))],
            '10-Year Bond': [4.75 for _ in range(len(dates))]
        })

try:
    raw_df = fetch_official_rbnz_rates()
    
    latest_row = raw_df.iloc[-1]
    max_date = latest_row['Date']
    
    st.subheader("Interactive Historical Scope")
    time_options = ["1 Month", "YTD", "1 Year", "2 Years", "5 Years", "Max"]
    selected_range = st.radio(
        "Select active lookback horizon window:",
        options=time_options,
        index=2, 
        horizontal=True
    )
    
    if selected_range == "1 Month":
        start_date = max_date - timedelta(days=30)
    elif selected_range == "YTD":
        start_date = datetime(max_date.year, 1, 1)
    elif selected_range == "1 Year":
        start_date = max_date - timedelta(days=365)
    elif selected_range == "2 Years":
        start_date = max_date - timedelta(days=365 * 2)
    elif selected_range == "5 Years":
        start_date = max_date - timedelta(days=365 * 5)
    else:
        start_date = raw_df['Date'].min()

    filtered_df = raw_df[(raw_df['Date'] >= start_date) & (raw_df['Date'] <= max_date)].copy()
    filtered_df.set_index('Date', inplace=True)

    st.write("---")

    # Layout graphics
    st.subheader("🏛️ Official Cash Rate (OCR) Trend")
    st.metric(label=f"Current Target Rate ({max_date.strftime('%d %b %Y')})", value=f"{latest_row['OCR']:.2f}%")
    st.line_chart(filtered_df[['OCR']])
    
    st.subheader("📈 90-Day Bank Bill Market Rate (BKBM)")
    st.metric(label=f"Current Market Close ({max_date.strftime('%d %b %Y')})", value=f"{latest_row['90-Day Bill']:.2f}%")
    st.line_chart(filtered_df[['90-Day Bill']])
    
    st.subheader("📊 10-Year Government Bond Yield Trend")
    st.metric(label=f"Current Benchmark Close ({max_date.strftime('%d %b %Y')})", value=f"{latest_row['10-Year Bond']:.2f}%")
    st.line_chart(filtered_df[['10-Year Bond']])
    
except Exception as global_err:
    st.error(f"Dashboard Display Interruption: {global_err}")
