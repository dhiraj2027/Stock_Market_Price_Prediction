import matplotlib.pyplot as plt
import streamlit as st

# Plot Full Timeline
def graph_actual_vs_predicted(valid_dates, actual, predicted, selected_date, selected_company):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(valid_dates, actual, label="Actual", linewidth=2)
    ax.plot(valid_dates, predicted, label="Predicted", linestyle="--")
    ax.axvline(x=selected_date, color='red', linestyle=':', label="Selected Date")
    ax.set_title(f"{selected_company} - Actual vs Predicted Prices")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
