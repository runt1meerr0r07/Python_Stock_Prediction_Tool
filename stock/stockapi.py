import yfinance as yf
import pandas as pd
import numpy as np

def fetch_stock_data(symbol="RELIANCE.NS"):
    
    if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
        symbol = f"{symbol}.NS"
    
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1y")  
    
    if hist.empty:
        return None  

    return {
        "price": round(hist["Close"].iloc[-1], 2),
        "historical_prices": hist["Close"].tolist(),
        "volume": hist["Volume"].iloc[-1],
        "sma_20": hist["Close"].rolling(window=20).mean().iloc[-1],
        "sma_50": hist["Close"].rolling(window=50).mean().iloc[-1],
        "sma_200": hist["Close"].rolling(window=200).mean().iloc[-1],
        "rsi": calculate_rsi(hist["Close"]),
        "currency": "₹", 
    }

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return round(100 - (100 / (1 + rs)).iloc[-1], 2)

if __name__ == "__main__":
    symbol = "RELIANCE.NS"  
    stock_data = fetch_stock_data(symbol)
    
    if stock_data:
        print(f"Stock Data for {symbol}:")
        for key, value in stock_data.items():
            print(f"{key}: {value}")
    else:
        print("Failed to fetch stock data.")
