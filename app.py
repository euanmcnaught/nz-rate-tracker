import streamlit as st
import pandas as pd

st.set_page_config(page_title="RBNZ Rates Monitor", layout="wide")
st.title("🇳🇿 Official RBNZ Data Monitor")

@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv('rates_data.csv')

try:
    df = load_data()
    df['Date'] = pd.to_datetime(df['Date'])
    st.line_chart(df.set_index('Date')[['OCR', '90-Day Bill', '10-Year Bond']])
    st.dataframe(df.tail(10))
except Exception:
    st.error("Data file 'rates_data.csv' not found. Please run the workflow in the Actions tab.")
