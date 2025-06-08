import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Display Results
def display_results(date_mask, selected_date, actual, predicted, mae, rmse, mape, r2):
    idx = np.where(date_mask)[0][0]
    actual_price = actual[idx]
    predicted_price = predicted[idx]


    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Selected Date", selected_date.strftime("%Y-%m-%d"))
    col2.metric("💰 Actual Price", f"${actual_price:.2f}")
    col3.metric("🔮 Predicted Price", f"${predicted_price:.2f}", delta=f"{(predicted_price - actual_price):.2f}")

    st.markdown("### 🔍 Evaluation Metrics")
    st.write(f"- **MAE**: `{mae:.4f}`")
    st.write(f"- **MAPE**: `{mape:.2f}%`")
    st.write(f"- **RMSE**: `{rmse:.4f}`")
    st.write(f"- **R² Score**: `{r2:.4f}`")