import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NZ Rates", layout="wide")
st.title("🇳🇿 Daily NZ Interest Rates")

RBNZ_URL = "https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_excel(RBNZ_URL, skiprows=4)
    df.dropna(subset=[df.columns[0]], inplace=True)
    df.rename(columns={
        df.columns[0]: 'Date',
        df.columns[1]: 'OCR',
        df.columns[5]: '60-Day Bill',
        df.columns[10]: '10-Year Bond'
    }, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    return df[['Date', 'OCR', '60-Day Bill', '10-Year Bond']].tail(60)

try:
    data = load_data()
    latest = data.iloc[-1]
    st.metric(label="Data Updated As Of", value=latest['Date'].strftime('%d %b %Y'))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Official Cash Rate", f"{latest['OCR']:.2f}%")
    col2.metric("60-Day Bank Bill", f"{latest['60-Day Bill']:.2f}%")
    col3.metric("10-Yr Gov Bond", f"{latest['10-Year Bond']:.2f}%")
    
    plot_df = data.melt(id_vars=['Date'], value_vars=['OCR', '60-Day Bill', '10-Year Bond'], 
                        var_name='Rate Type', value_name='Yield (%)')
    fig = px.line(plot_df, x='Date', y='Yield (%)', color='Rate Type')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error("RBNZ server connection timed out. Please try refreshing.")
