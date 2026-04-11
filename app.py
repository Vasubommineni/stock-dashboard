from flask import Flask, jsonify, request, render_template
import yfinance as yf
import pandas as pd

app = Flask(__name__)

companies = {
    "INFY": "INFY.NS",
    "TCS": "TCS.NS",
    "RELIANCE": "RELIANCE.NS"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/companies")
def get_companies():
    return jsonify(list(companies.keys()))

@app.route("/data/<symbol>")
def get_data(symbol):
    ticker = companies.get(symbol.upper())

    if not ticker:
        return jsonify({"error": "Invalid symbol"})

    data = yf.download(ticker, period="30d")

    data.columns = data.columns.get_level_values(0)

    data['Daily Return'] = (data['Close'] - data['Open']) / data['Open']
    data['MA7'] = data['Close'].rolling(7).mean()

    data = data.reset_index()

    return data.to_json(orient="records")

@app.route("/summary/<symbol>")
def get_summary(symbol):
    ticker = companies.get(symbol.upper())

    if not ticker:
        return jsonify({"error": "Invalid symbol"})

    data = yf.download(ticker, period="1y")

    summary = {
        "52_week_high": float(data['High'].max()),
        "52_week_low": float(data['Low'].min()),
        "average_close": float(data['Close'].mean())
    }

    return jsonify(summary)

if __name__ == "__main__":
    app.run(debug=True)