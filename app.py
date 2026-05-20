import streamlit as st
import yfinance as ticker
from datetime import datetime, timedelta

st.set_page_config(page_title="NZ Rates App", layout="wide")
st.title("🇳🇿 Live NZ Interest Rates")
st.caption("Firewall-free data served directly via Yahoo Finance API")

@st.cache_data(ttl=1800)
def fetch_nz_rates():
    # ^NZ90D = New Zealand 90-Day Bank Bill Yield
    # ^NZ10 = New Zealand 10-Year Government Bond Yield
    tickers = {"90-Day Bank Bill": "^NZ90D", "10-Year Bond": "^NZ10"}
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=90)
    
    combined_df = []
    
    for label, sym in tickers.items():
        t = ticker.Ticker(sym)
        df = t.history(start=start_date, end=end_date)
        if not df.empty:
            df = df[['Close']].rename(columns={'Close': label})
            combined_df.append(df)
            
    if combined_df:
        final_df = combined_df[0]
        for additional_df in combined_df[1:]:
            final_df = final_df.join(additional_df, how='outer')
        final_df.index = final_df.index.date
        final_df = final_df.ffill().dropna()
        return final_df
    return None

try:
    data = fetch_nz_rates()
    
    if data is not None and not data.empty:
        latest_date = data.index[-1]
        latest_rates = data.iloc[-1]
        
        st.metric(label="Market Last Updated", value=latest_date.strftime('%d %b %Y'))
        
        # Display clear mobile metric cards
        col1, col2 = st.columns(2)
        col1.metric("90-Day Bank Bill", f"{latest_rates['90-Day Bank Bill']:.2f}%")
        col2.metric("10-Yr Government Bond", f"{latest_rates['10-Year Bond']:.2f}%")
        
        # Interactive Mobile Chart
        st.subheader("Historical Trajectory (Past 90 Days)")
        st.line_chart(data)
    else:
        st.error("No market data returned. The financial markets may be closed.")
        
except Exception as e:
    st.error(f"API Connection Error: {e}")
