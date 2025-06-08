# app/model_handler.py
from keras.models import load_model
import numpy as np
import streamlit as st

@st.cache_resource
def load_lstm_model(model_path):
    return load_model(model_path)

def predict(model, X, scaler):
    pred_scaled = model.predict(X)
    # Create a dummy array of shape (n_samples, 6)
    # Fill all values with 0, then replace only the first column with predicted close prices
    dummy = np.zeros((pred_scaled.shape[0], 6))
    dummy[:, 0] = pred_scaled[:, 0]  # predicted Close prices in 1st column

    # Inverse transform the dummy array
    inverted = scaler.inverse_transform(dummy)

    # Extract only the Close price
    pred = inverted[:, 0]
    return pred