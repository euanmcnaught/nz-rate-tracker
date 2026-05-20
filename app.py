import streamlit as st
import pandas as pd

st.set_page_config(page_title="RBNZ Rates Monitor", layout="wide")
st.title("🇳🇿 Official RBNZ Data Monitor")

# Because we are using the CSV created by your GitHub Action, 
# this load function is now extremely fast and error-proof.
@st.cache_data(ttl=3600)
def load_data():
    # It reads the file that your GitHub Action keeps updated
    df = pd.read_csv('rates_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Load and display
try:
    df = load_data()
    st.success("Data successfully loaded from local repository.")
    
    # Simple line chart
    st.line_chart(df.set_index('Date')[['OCR', '90-Day Bill', '10-Year Bond']])
    
    # Display table
    st.write("Recent Data Points:")
    st.dataframe(df.tail(10))
    
except Exception as e:
    st.error("The data file 'rates_data.csv' is missing or not yet generated.")
