import numpy as np
import pandas as pd
from stock.stockapi import fetch_stock_data

def calculate_bollinger_bands(prices, window=20):
    """Calculate Bollinger Bands for a price series"""
    prices_series = pd.Series(prices)
    sma = prices_series.rolling(window=window).mean()
    std = prices_series.rolling(window=window).std()
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    
    if len(upper_band) > 0 and len(lower_band) > 0:
        return upper_band.iloc[-1], lower_band.iloc[-1]
    return None, None

def calculate_rsi(prices, window=14):
    """Calculate RSI for a price series"""
    prices_series = pd.Series(prices)
    delta = prices_series.diff()
    
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
  
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    
    rs = avg_gain / avg_loss
    
    rsi = 100 - (100 / (1 + rs))
    
    if len(rsi) > 0:
        return round(rsi.iloc[-1], 2)
    return 50  

def predict_stock(symbol="RELIANCE.NS"):
    """Generate stock prediction based on technical indicators"""
    data = fetch_stock_data(symbol)
    if data is None:
        return None

    prices = data.get("historical_prices", [])
    if not prices:
        return None
        
    volumes = data.get("volumes", [])
    
   
    prices_series = pd.Series(prices)
    
    current_price = data.get('price', 0)
    if current_price is None:
        current_price = 0
        
    sma_20 = data.get('sma_20', current_price)
    if sma_20 is None:
        sma_20 = current_price
        
    sma_50 = data.get('sma_50', current_price)
    if sma_50 is None:
        sma_50 = current_price
        
    sma_200 = data.get('sma_200', current_price)
    if sma_200 is None:
        sma_200 = current_price
    
    
    rsi = data.get('rsi')
    if rsi is None:
        rsi = calculate_rsi(prices)
    
    
    upper_band, lower_band = calculate_bollinger_bands(prices)
    if upper_band is None or lower_band is None:
        upper_band = sma_20 * 1.05  
        lower_band = sma_20 * 0.95  
    
    score = 0
    
    if current_price <= lower_band:
        score += 0.3  
    elif current_price >= upper_band:
        score -= 0.3  
    

    if rsi < 30:
        score += 0.25  
    elif rsi > 70:
        score -= 0.25  
    
    if sma_50 > sma_200:
        score += 0.25 
    elif sma_50 < sma_200:
        score -= 0.25  
    
    if volumes and len(volumes) > 10:
        avg_volume = sum(volumes[-10:]) / 10
        latest_volume = volumes[-1]
        if latest_volume > (1.5 * avg_volume):
            score += 0.2  # Bullish - high volume
    

    if score >= 0.5:
        prediction = "Strong Buy"
    elif score >= 0.15:
        prediction = "Buy"
    elif score > -0.15:
        prediction = "Hold"
    elif score > -0.5:
        prediction = "Sell"
    else:
        prediction = "Strong Sell"
    

    price_std = prices_series.std() if len(prices_series) > 1 else current_price * 0.05

    if prediction == "Strong Buy":
        target_price = sma_20 + (0.7 * price_std)
    elif prediction == "Buy":
        target_price = sma_20 + (0.3 * price_std)
    elif prediction == "Hold":
        target_price = current_price
    elif prediction == "Sell":
        target_price = sma_20 - (0.3 * price_std)
    else: 
        target_price = sma_20 - (0.7 * price_std)
    
    return {
        "prediction": prediction,
        "score": score,
        "target_price": target_price
    }

if __name__ == "__main__":
    result = predict_stock("RELIANCE.NS")
    print(result)