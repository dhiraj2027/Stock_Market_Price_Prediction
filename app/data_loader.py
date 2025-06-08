# app/data_loader.py
import pandas as pd
from pathlib import Path
import streamlit as st

@st.cache_data
def load_data(path):
    if not Path(path).exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=["Company", "Date"]).dropna(subset=['Date'])
    return df

def get_company_data(df, company):
    return df[df['Company'] == company].copy()