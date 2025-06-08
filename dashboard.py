# frontend/dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
from app.data_loader import load_data, get_company_data
from app.indicators import add_technical_indicators
from app.preprocessing import scale_and_create_sequences
from app.model_handler import load_lstm_model, predict
from app.evaluator import evaluate_predictions
from front.results import display_results
from front.plot_graph import graph_actual_vs_predicted
import os

st.set_page_config(
    page_title="Stock Market Price Prediction",
    page_icon="📈",
    layout="wide"
)

# --- Load data and model ---
DATA_PATH = "data/stock_details_5_years.csv"
MODEL_PATH = "models/lstm_stock_model_with_indicators.keras"

st.title("📈 Stock Market Price Prediction")
st.markdown("An advanced LSTM-based multi-company prediction dashboard with technical indicators.")

# --- Data Loading ---
try:
    df = load_data(DATA_PATH)
    companies = df['Company'].unique().tolist()
except Exception as e:
    st.error(f"⚠️ Failed to load data: {e}")
    st.stop()


# --- Sidebar ---
st.sidebar.title("Configuration")
selected_company = st.sidebar.selectbox("Select Company", companies)

# --- Filtered company data ---
company_df = get_company_data(df, selected_company)
company_df = add_technical_indicators(company_df)
company_df.dropna(inplace=True)

# --- Date Selection ---
min_date = company_df['Date'].min().to_pydatetime()
max_date = company_df['Date'].max().to_pydatetime()
selected_date = st.sidebar.date_input(
    "Select Date for Prediction",
    min_value=min_date,
    max_value=max_date,
    value=min_date
)

show_raw_data = st.sidebar.checkbox("Show Raw Data")

# --- Model Input Prep ---
time_steps = 50
X, y_scaled, scaler, valid_dates = scale_and_create_sequences(company_df, time_step=time_steps)
dates = company_df['Date'].values[time_steps:]

# --- Load model and predict ---
model = load_lstm_model(MODEL_PATH)
predicted = predict(model, X, scaler)

# Inverse transform actual y values
dummy_y = np.column_stack((y_scaled, np.zeros((len(y_scaled), 5))))
actual = scaler.inverse_transform(dummy_y)[:, 0]

# Find the index of the selected date
selected_date = pd.to_datetime(selected_date)
date_mask = (valid_dates == selected_date)
if not any(date_mask):
    st.error(f"⚠️ No prediction available for {selected_date.strftime('%Y-%m-%d')}. Try another date.")
else:
    mae, rmse, mape, r2 = evaluate_predictions(actual, predicted)

    # --- Display Results ---
    st.subheader(f"📊Stock Price Prediction: {selected_company}")
    display_results(date_mask, selected_date, actual, predicted, mae, rmse, mape, r2)

    # Plot actual vs predicted
    graph_actual_vs_predicted(valid_dates, actual, predicted, selected_date, selected_company)

    # Raw data
    if show_raw_data:
        st.dataframe(company_df)