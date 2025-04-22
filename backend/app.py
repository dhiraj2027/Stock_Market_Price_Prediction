from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Load dataset
df = pd.read_csv("stock_details_5_years.csv")
df["Company"] = df["Company"].astype(str).str.strip().str.upper()

df["Date"] = pd.to_datetime(df["Date"]).dt.date
df = df.sort_values(by=["Company", "Date"])
companies = df["Company"].unique()
model = load_model("lstm_stock_model_with_indicators.keras")
sequence_length = 50
features = ["Close", "SMA_10", "SMA_50", "EMA_10", "EMA_50", "RSI"]

# RSI function
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Technical indicators
def add_technical_indicators(data):
    data["SMA_10"] = data["Close"].rolling(window=10).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["EMA_10"] = data["Close"].ewm(span=10, adjust=False).mean()
    data["EMA_50"] = data["Close"].ewm(span=50, adjust=False).mean()
    data["RSI"] = compute_rsi(data["Close"], 14)
    return data

# Preprocess
df = df.groupby("Company", group_keys=False).apply(add_technical_indicators).reset_index(drop=True)
df.dropna(inplace=True)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_company = data.get("company", "").strip().upper()
    input_date_str = data.get("date", "").strip()

    try:
        input_date = datetime.strptime(input_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    normalized_companies = [c.strip().upper() for c in companies]
    if input_company not in normalized_companies:
        return jsonify({"error": "Company not found"}), 404

    matched_company = companies[normalized_companies.index(input_company)]
    company_data = df[df["Company"] == matched_company].copy()
    company_data.sort_values("Date", inplace=True)

    if input_date not in company_data["Date"].values:
        return jsonify({"error": "Date not found in dataset for this company"}), 404

    target_idx = company_data[company_data["Date"] == input_date].index[0]
    if target_idx < sequence_length:
        return jsonify({"error": "Not enough data before this date for prediction"}), 400

    sequence_data = company_data.loc[target_idx - sequence_length:target_idx - 1, features].values

    scaler = MinMaxScaler()
    scaler.fit(company_data[features])  # Fit on entire company data
    sequence_scaled = scaler.transform(sequence_data)

    predictions = []
    input_seq = sequence_scaled.copy()

    for _ in range(10):  # Predict next 10 days
        X_input = np.expand_dims(input_seq, axis=0)
        pred_scaled = model.predict(X_input)[0][0]

        dummy = np.zeros((1, len(features)))
        dummy[0, 0] = pred_scaled
        pred_price = scaler.inverse_transform(dummy)[0][0]
        predictions.append(pred_price)

        # Simulate next day for sequential prediction
        new_row = np.copy(input_seq[-1])
        new_row[0] = pred_scaled
        input_seq = np.vstack([input_seq[1:], new_row])

    actual_prices = company_data.loc[target_idx + 1: target_idx + 10, "Close"].values.tolist()

    return jsonify({
        "company": matched_company,
        "date": input_date_str,
        "predicted_close_prices_next_10_days": [round(p, 2) for p in predictions],
        "actual_close_prices_next_10_days": [round(p, 2) for p in actual_prices]
    })

if __name__ == '__main__':
    app.run(debug=True)
