# PortfolioTracker

A **desktop stock prediction and tracking app** built with **PyQt6** and **SQLite3**. The app provides **technical analysis-based predictions** using **Bollinger Bands, RSI, Moving Averages, Volume indicators**, and **live data & news**. It helps users make informed decisions on buying, selling, or holding stocks.

---

## Features

- **PyQt6 GUI** for interactive desktop experience  
- **SQLite3** database to store stock data  
- Fetches **live stock data** using **yfinance**  
- Fetches **live business news** from **NewsData API**  
- Calculates key **technical indicators**:  
  - RSI (Relative Strength Index)  
  - Bollinger Bands  
  - Moving Averages (SMA 20, 50, 200)  
  - Volume analysis  
- Generates **buy/sell/hold recommendations** with confidence scores  
- Computes **target prices** based on volatility and moving averages  

---

## Stock Prediction Logic

### 1. Data Collection
- Historical stock data (1 year of daily closing prices)  
- Trading volume  
- Simple Moving Averages (20-day, 50-day, 200-day)  
- Live stock data using `yfinance`  

### 2. Technical Indicators

| Indicator | Description | Usage |
|-----------|------------|-------|
| RSI | Momentum oscillator (0–100) | RSI < 30 → bullish, RSI > 70 → bearish |
| Bollinger Bands | Volatility bands around SMA 20 | Price near upper band → overbought, lower band → oversold |
| Moving Averages | SMA 20, 50, 200 | Golden Cross (SMA 50 > SMA 200) → bullish, Death Cross → bearish |
| Volume | Trading volume analysis | Unusually high volume → potentially bullish |

### 3. Score Calculation System

| Component | Condition | Score |
|-----------|----------|-------|
| Bollinger Bands | Price ≤ lower band | +0.3 |
|  | Price ≥ upper band | -0.3 |
| RSI | <30 | +0.25 |
|  | >70 | -0.25 |
| Moving Average Cross | Golden Cross | +0.25 |
|  | Death Cross | -0.25 |
| Volume | High volume (>1.5× avg) | +0.2 |

- Total score ranges **-0.8 (extremely bearish) to +0.8 (extremely bullish)**  

### 4. Prediction Categories

| Score | Recommendation |
|-------|----------------|
| ≥ 0.5 | Strong Buy |
| 0.15 – 0.5 | Buy |
| -0.15 – 0.15 | Hold |
| -0.5 – -0.15 | Sell |
| ≤ -0.5 | Strong Sell |

### 5. Target Price Calculation

- Uses **20-day SMA** as base and **price standard deviation** for volatility.  
- Strong Buy: `SMA 20 + 70% of SD`  
- Buy: `SMA 20 + 30% of SD`  
- Hold: Current price  
- Sell: `SMA 20 - 30% of SD`  
- Strong Sell: `SMA 20 - 70% of SD`  

**Two types of standard deviation used:**  

- **Rolling SD (Bollinger Bands):** short-term, adapts to recent trends  
- **Global SD (Target Price):** long-term, stable measure of overall volatility  

---

## Live News Feature

- Fetches **business news** from NewsData API  
- Categorizes news into **Market Updates, Investing, Company News, Regulations, Economy, Crypto, Banking, Others**  
- Allows **searching news by keywords**  
- Displayed in a **scrollable PyQt6 GUI**  

---

## Installation

```bash
# Clone the repo
git clone git@github-secondary:SecondaryAccount/PortfolioTracker.git
cd PortfolioTracker

# Install dependencies
pip install PyQt6 pandas numpy matplotlib yfinance requests

