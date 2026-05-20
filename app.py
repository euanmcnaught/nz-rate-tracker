import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NZ Rates", layout="wide")
st.title("🇳🇿 Live NZ Interest Rates")
st.caption("Rate limit free data served via the open Stooq Financial Database")

@st.cache_data(ttl=3600)
def fetch_stooq_data():
    # Stooq tickers for New Zealand benchmarks
    # 10NZD.B = 10 Year Government Bond Yield
    # 3MNZD.M = 3 Month / 90 Day Money Market Rate (Moves identical to 60-day)
    tickers = {
        "10-Year Bond": "https://stooq.com/q/d/l/?s=10nzd.b&i=d",
        "90-Day Bill": "https://stooq.com/q/d/l/?s=3mnzd.m&i=d"
    }
    
    combined_df = []
    
    for label, url in tickers.items():
        try:
            # Download the CSV raw data stream directly from Stooq
            df = pd.read_csv(url, parse_dates=['Date'], index_col='Date')
            if not df.empty:
                # We extract the 'Close' yield percentage column
                df = df[['Close']].rename(columns={'Close': label})
                combined_df.append(df)
        except Exception:
            continue
            
    if combined_df:
        # Join the datasets side-by-side on their dates
        final_df = combined_df[0]
        for additional_df in combined_df[1:]:
            final_df = final_df.join(additional_df, how='outer')
        
        # Sort chronologically, forward-fill missing weekend values, and grab past 60 days
        final_df = final_df.sort_index().ffill().dropna()
        return final_df.tail(60)
    return None

try:
    data = fetch_stooq_data()
    
    if data is not None and not data.empty:
        latest_date = data.index[-1]
        latest_rates = data.iloc[-1]
        
        st.metric(label="Market Last Updated", value=latest_date.strftime('%d %b %Y'))
        
        # Display clean layout metrics
        col1, col2 = st.columns(2)
        col1.metric("90-Day Bank Bill Yield", f"{latest_rates['90-Day Bill']:.2f}%")
        col2.metric("10-Yr Government Bond", f"{latest_rates['10-Year Bond']:.2f}%")
        
        # Dynamic line graph matching mobile dimensions
        st.subheader("Historical Yield Trend (Past 60 Days)")
        
        plot_df = data.reset_index().melt(id_vars=['index'], value_vars=['90-Day Bill', '10-Year Bond'], 
                                var_name='Rate Type', value_name='Yield (%)')
        plot_df.rename(columns={'index': 'Date'}, inplace=True)
        
        fig = px.line(plot_df, x='Date', y='Yield (%)', color='Rate Type')
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to collect historical financial streams from data node.")
        
except Exception as e:
    st.error(f"System Error: {e}")
