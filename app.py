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
    symbol = symbol.upper()

    # If user enters plain name, add .NS
    if "." not in symbol:
        symbol = symbol + ".NS"

    ticker = companies.get(symbol.replace(".NS", ""), symbol)

    if not ticker:
        return jsonify({"error": "Invalid symbol"})
    
    range_param = request.args.get("range", "30")

    range_map = {
        "7": "7d",
        "30": "30d",
        "90": "3mo"
    }

    period = range_map.get(range_param, "30d")

    data = yf.download(ticker, period=period)

    if data.empty:
        return jsonify({"error": "No data found for this symbol"})
    
    data.columns = data.columns.get_level_values(0)

    data['Daily Return'] = (data['Close'] - data['Open']) / data['Open']
    data['MA7'] = data['Close'].rolling(7).mean()

    data['Prediction'] = data['Close'].rolling(3).mean()

    data = data.reset_index()

    data = data.bfill().ffill()

    return jsonify(data.to_dict(orient="records"))

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

@app.route("/compare")
def compare():
    symbol1 = request.args.get("symbol1")
    symbol2 = request.args.get("symbol2")

    ticker1 = companies.get(symbol1.upper())
    ticker2 = companies.get(symbol2.upper())

    if not ticker1 or not ticker2:
        return {"error": "Invalid symbols"}

    data1 = yf.download(ticker1, period="30d")
    data2 = yf.download(ticker2, period="30d")

    # FIX columns
    data1.columns = data1.columns.get_level_values(0)
    data2.columns = data2.columns.get_level_values(0)

    data1 = data1.reset_index()
    data2 = data2.reset_index()

    return {
        "stock1": data1.to_dict(orient="records"),
        "stock2": data2.to_dict(orient="records")
    }

if __name__ == "__main__":
    app.run(debug=True)