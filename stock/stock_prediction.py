import numpy as np
import pandas as pd
from stock.stockapi import fetch_stock_data

def calculate_bollinger_bands(prices, window=20):
    sma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    return upper_band.iloc[-1], lower_band.iloc[-1]

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return round(100 - (100 / (1 + rs)).iloc[-1], 2)

def predict_stock(symbol="RELIANCE.NS"):
    data = fetch_stock_data(symbol)
    if data is None:
        return None

    prices = pd.Series(data["historical_prices"])
   
    upper_band, lower_band = calculate_bollinger_bands(prices)
    rsi = calculate_rsi(prices)
    sma_20 = data["sma_20"]
    sma_50 = data["sma_50"]
    sma_200 = data["sma_200"]
    volume = data["volume"]

    
    score_components = {
        "bollinger": 0,
        "rsi": 0,
        "ma_cross": 0,
        "volume": 0
    }
    
    if prices.iloc[-1] <= lower_band:
        score_components["bollinger"] = 0.3
    elif prices.iloc[-1] >= upper_band:
        score_components["bollinger"] = -0.3
        
  
    if rsi < 30:
        score_components["rsi"] = 0.25
    elif rsi > 70:
        score_components["rsi"] = -0.25
        
    
    if sma_50 > sma_200:
        score_components["ma_cross"] = 0.25
    elif sma_50 < sma_200:
        score_components["ma_cross"] = -0.25
        
    
    avg_volume = np.mean(prices.rolling(window=30).mean())
    if volume > 1.5 * avg_volume:
        score_components["volume"] = 0.2

    
    score = sum(score_components.values())


    if score >= 0.5:  
        prediction = "Strong Buy"
        target_price = sma_20 + (0.7 * np.std(prices))  
    elif 0.15 <= score < 0.5:  
        prediction = "Buy"
        target_price = sma_20 + (0.3 * np.std(prices))  
    elif -0.15 < score < 0.15:  
        prediction = "Hold"
        target_price = prices.iloc[-1]
    elif -0.5 < score <= -0.15:  
        prediction = "Sell"
        target_price = sma_20 - (0.3 * np.std(prices))  
    else:
        prediction = "Strong Sell"
        target_price = sma_20 - (0.7 * np.std(prices)) 

    return {
        "prediction": prediction,
        "score": round(score, 2),
        "score_breakdown": score_components,
        "target_price": round(target_price, 2),
        "indicators": {
            "rsi": rsi,
            "upper_band": round(upper_band, 2),
            "lower_band": round(lower_band, 2),
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "sma_200": round(sma_200, 2)
        }
    }

if __name__ == "__main__":
    result = predict_stock("RELIANCE.NS")
    print(result)
