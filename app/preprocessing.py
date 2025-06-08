# app/preprocessing.py
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

@st.cache_data
def scale_and_create_sequences(df, time_step=50):
    # exactly the 6 features (in the same order used during training)
    feature_cols = ['Close','SMA_10','SMA_50','EMA_10','EMA_50','RSI']
    data = df[feature_cols].values  # shape: (n_rows, 6)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    X, y = [], []
    for i in range(time_step, len(scaled)):
        X.append(scaled[i-time_step:i])    # (time_step, 6)
        y.append(scaled[i, 0])           # predicting the 'Close' feature

    X = np.array(X)  # -> (samples, time_step, 6)
    y = np.array(y)  # -> (samples,)
    valid_date = df['Date'].iloc[time_step:]
    return X, y, scaler, valid_date
