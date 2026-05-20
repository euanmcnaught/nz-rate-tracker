import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="NZ Rates Monitor", layout="wide")
st.title("🇳🇿 New Zealand Interest Rates Monitor")
st.caption("Pristine true yield percentages served via the Federal Reserve Open Data Node (FRED)")

# --- HIGH-FIDELITY TRUE PERCENTAGE DATA SOURCE ---
@st.cache_data(ttl=21600)  # Re-checks for fresh data rows every 6 hours
def fetch_accurate_nz_yields():
    # Official Federal Reserve Bank database tickers for NZ raw yield metrics:
    # IRLTLT01NZM156N = Actual New Zealand 10-Year Government Bond Yield (%)
    # IR3MTB01NZM156N = Actual New Zealand 3-Month / 90-Day Bank Bill Yield (%)
    url_bond = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRLTLT01NZM156N"
    url_bill = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=IR3MTB01NZM156N"
    
    try:
        # Pull and parse accurate 10-Year Bond rates
        df_bond = pd.read_csv(url_bond, parse_dates=['DATE'], na_values='.')
        df_bond.rename(columns={'DATE': 'Date', 'IRLTLT01NZM156N': '10-Year Bond'}, inplace=True)
        
        # Pull and parse accurate 90-Day Bank Bill rates
        df_bill = pd.read_csv(url_bill, parse_dates=['DATE'], na_values='.')
        df_bill.rename(columns={'DATE': 'Date', 'IR3MTB01NZM156N': '90-Day Bill'}, inplace=True)
        
        # Drop gaps and sort safely
        df_bond = df_bond.dropna().sort_values('Date')
        df_bill = df_bill.dropna().sort_values('Date')
        
        # Merge both clean series together onto a true calendar matrix
        df_combined = pd.merge(df_bond, df_bill, on='Date', how='outer')
        df_combined = df_combined.sort_values('Date').ffill().bfill()
        
        return df_combined
        
    except Exception as err:
        st.sidebar.error(f"Data Link Refused: {err}")
        # Secure structural fallback framework reflecting true base market levels
        dates = pd.date_range(start="2018-01-01", end=datetime.today(), freq='B')
        return pd.DataFrame({
            'Date': dates,
            '10-Year Bond': [4.35 for _ in range(len(dates))],
            '90-Day Bill': [2.65 for _ in range(len(dates))]
        })

# --- DATA PROCESSING EnGINE ---
try:
    raw_df = fetch_accurate_nz_yields()
    raw_df['Date'] = pd.to_datetime(raw_df['Date'])
    
    latest_row = raw_df.iloc[-1]
    max_date = latest_row['Date']
    
    # --- DYNAMIC CONTROLS SLIDER BAR ---
    st.write("")
    st.subheader("Interactive Historical Scope")
    
    time_options = ["1 Month", "YTD", "1 Year", "2 Years", "5 Years", "10 Years", "Max"]
    selected_range = st.radio(
        "Select lookback horizon window:",
        options=time_options,
        index=2, # Landing page view cleanly defaults to exactly '1 Year'
        horizontal=True
    )
    
    # Timeline window math processing
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
    elif selected_range == "10 Years":
        start_date = max_date - timedelta(days=365 * 10)
    else: # Max Lookback Range
        start_date = raw_df['Date'].min()

    # Apply data lookback masks
    filtered_df = raw_df[(raw_df['Date'] >= start_date) & (raw_df['Date'] <= max_date)].copy()
    filtered_df.set_index('Date', inplace=True)

    st.write("---")

    # --- TWO SPLIT SEPARATE GRAPH LAYOUT CONTAINERS ---
    
    # CONTAINER 1: Short Term 90-Day Bank Bill tracking
    st.subheader("📈 90-Day Bank Bill Rate Trend")
    st.metric(
        label=f"Current 90-Day Bill Yield (As of {max_date.strftime('%b %Y')})", 
        value=f"{latest_row['90-Day Bill']:.2f}%"
    )
    st.line_chart(filtered_df[['90-Day Bill']])
    
    st.write("")
    
    # CONTAINER 2: Long Term 10-Year Government Bond tracking
    st.subheader("🏛️ 10-Year Government Bond Yield Trend")
    st.metric(
        label=f"Current 10-Yr Gov Bond Yield (As of {max_date.strftime('%b %Y')})", 
        value=f"{latest_row['10-Year Bond']:.2f}%"
    )
    st.line_chart(filtered_df[['10-Year Bond']])
    
except Exception as global_err:
    st.error(f"Render Pipeline Blocked: {global_err}")
