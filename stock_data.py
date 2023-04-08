# stock_data.py
import json
import contextlib
import requests

API_KEY = "E5IFHXM036FQRFN9"

with open('tickers.json', 'r') as f:
    data = json.load(f)
    
list_of_tickers = data['tickers']

def get_stock_data(symbol: str, interval: str) -> dict:
    url = f"https://www.alphavantage.co/query?function={interval}&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Error occurred!")

    json_data = response.json()
    if "Time Series (Daily)" in json_data:
        return json_data["Time Series (Daily)"]
    elif "Weekly Adjusted Time Series" in json_data:
        return json_data["Weekly Adjusted Time Series"]
    elif "Monthly Adjusted Time Series" in json_data:
        return json_data["Monthly Adjusted Time Series"]
    else:
        raise Exception("Unexpected data format")


def extract_data(data: dict) -> tuple:
    closing_prices, dates, opening_prices, high_prices, low_prices, volumes = [], [], [], [], [], []

    for date, values in data.items():
        with contextlib.suppress(ValueError):
            closing_prices.append(float(values.get("4. close", 0)))
            dates.append(date)
            opening_prices.append(float(values.get("1. open", 0)))
            high_prices.append(float(values.get("2. high", 0)))
            low_prices.append(float(values.get("3. low", 0)))
            volumes.append(float(values.get("6. volume", 0)))
    return closing_prices[::-1], dates[::-1], opening_prices[::-1], high_prices[::-1], low_prices[::-1], volumes[::-1]
