from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QProgressBar, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from datetime import datetime
import random

class MarketSummaryWidget(QFrame):
    def __init__(self, parent=None):
        super(MarketSummaryWidget, self).__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("background-color: #2a2e39; border: 1px solid #616161; border-radius: 5px;")
        self.setFixedWidth(300)  # Set fixed width to maintain proportions
        
        self.init_ui()
        # Update only once at startup, no timer for random updates
        self.update_summary()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)  # More vertical padding
        layout.setSpacing(12)  # Increase spacing between elements
        
        # Market Summary Title - Remove box completely
        title = QLabel("Market Summary")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0; background-color: transparent; border: none;")
        title.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Add spacing instead of a visible widget
        layout.addSpacing(5)
        
        # Indices grid (more compact)
        indices_grid = QGridLayout()
        indices_grid.setSpacing(8)  # Increase spacing
        indices_grid.setContentsMargins(0, 2, 0, 2)  # Reduce vertical margins
        
        # Use slightly larger font
        font_style = "font-size: 13px; "
        value_style = font_style + "font-weight: bold;"
        
        self.nifty_label = QLabel("NIFTY 50:")
        self.nifty_label.setStyleSheet(font_style + "color: #e0e0e0;")
        self.nifty_value = QLabel("--")
        self.nifty_value.setStyleSheet(value_style + "color: #e0e0e0;")
        
        self.sensex_label = QLabel("SENSEX:")
        self.sensex_label.setStyleSheet(font_style + "color: #e0e0e0;")
        self.sensex_value = QLabel("--")
        self.sensex_value.setStyleSheet(value_style + "color: #e0e0e0;")
        
        self.nifty_bank_label = QLabel("NIFTY BANK:")
        self.nifty_bank_label.setStyleSheet(font_style + "color: #e0e0e0;")
        self.nifty_bank_value = QLabel("--")
        self.nifty_bank_value.setStyleSheet(value_style + "color: #e0e0e0;")
        
        self.market_status = QLabel("Market Status: Open")
        self.market_status.setStyleSheet(font_style + "color: #e0e0e0;")
        
        # Original arrangement
        indices_grid.addWidget(self.nifty_label, 0, 0)
        indices_grid.addWidget(self.nifty_value, 0, 1)
        indices_grid.addWidget(self.sensex_label, 1, 0)
        indices_grid.addWidget(self.sensex_value, 1, 1)
        indices_grid.addWidget(self.nifty_bank_label, 2, 0)
        indices_grid.addWidget(self.nifty_bank_value, 2, 1)
        indices_grid.addWidget(self.market_status, 3, 0, 1, 2)  # Span 2 columns
        
        layout.addLayout(indices_grid)
        
        # Add spacing instead of a visible widget
        layout.addSpacing(10)
        
        # Sentiment bar - Remove box completely
        sentiment_layout = QVBoxLayout()
        sentiment_layout.setSpacing(5)  # Increased spacing
        sentiment_layout.setContentsMargins(0, 0, 0, 0)
        
        sentiment_label = QLabel("Market Sentiment:")
        sentiment_label.setStyleSheet(font_style + "color: #e0e0e0; background-color: transparent; border: none;")
        sentiment_label.setContentsMargins(0, 0, 0, 0)
        sentiment_layout.addWidget(sentiment_label, 0, Qt.AlignmentFlag.AlignLeft)
        
        self.sentiment_bar = QProgressBar()
        self.sentiment_bar.setRange(0, 100)
        self.sentiment_bar.setValue(50)
        self.sentiment_bar.setTextVisible(True)
        self.sentiment_bar.setFormat("%p% Neutral")
        self.sentiment_bar.setFixedHeight(22)  # Larger height for better visibility
        self.sentiment_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2e39; 
                color: #ffffff; 
                border: 1px solid #616161; 
                border-radius: 4px;
                text-align: center;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #ffab40;
                border-radius: 4px;
            }
        """)
        
        sentiment_layout.addWidget(self.sentiment_bar)
        layout.addLayout(sentiment_layout)
        
        # Add spacing instead of a visible widget
        layout.addSpacing(10)
        
        # Last updated
        self.last_updated = QLabel("Last updated: --")
        self.last_updated.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        self.last_updated.setFixedHeight(15)
        self.last_updated.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.last_updated)
        
        self.setLayout(layout)
        self.update_summary()
        
    def update_summary(self):
        try:
            # Get real market data from stock predictions instead of random numbers
            from stock.stockapi import fetch_stock_data
            from stock.stock_prediction import predict_stock
            import threading
            
            # Update market status based on current time
            now = datetime.now()
            market_open = now.weekday() < 5 and (9 <= now.hour < 15 or (now.hour == 15 and now.minute < 30))
            
            if market_open:
                self.market_status.setText("Market Status: Open")
                self.market_status.setStyleSheet("color: #00c853; font-weight: bold;")
            else:
                self.market_status.setText("Market Status: Closed")
                self.market_status.setStyleSheet("color: #ff5252; font-weight: bold;")
            
            # Market index symbols - should be replaced with actual index symbols when available
            # For now, we'll calculate indices based on baskets of stocks
            nifty_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
            sensex_stocks = ["HDFCBANK.NS", "INFY.NS", "ITC.NS", "KOTAKBANK.NS", "AXISBANK.NS"]
            bank_stocks = ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS"]
            
            # Calculate index values based on stock performance
            self.update_index_from_stocks("NIFTY 50", nifty_stocks, self.nifty_value)
            self.update_index_from_stocks("SENSEX", sensex_stocks, self.sensex_value)
            self.update_index_from_stocks("NIFTY BANK", bank_stocks, self.nifty_bank_value)
            
            # List of all top Indian stocks to analyze for sentiment
            top_stocks = [
                "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
                "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS",
                "KOTAKBANK.NS", "AXISBANK.NS", "LT.NS", "MARUTI.NS", "TATASTEEL.NS",
                "HDFC.NS", "WIPRO.NS", "ONGC.NS", "ADANIENT.NS", "SUNPHARMA.NS"
            ]
            
            # Calculate market sentiment based on prediction scores
            # This is done in a separate thread to avoid UI freezing
            threading.Thread(target=self.calculate_market_sentiment, args=(top_stocks,), daemon=True).start()
            
            # Update timestamp
            self.last_updated.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"Error updating market summary: {e}")
            
    def update_index_from_stocks(self, index_name, stocks, label_widget):
        """Calculate and update index value based on a basket of stocks"""
        try:
            from stock.stockapi import fetch_stock_data
            
            prices_change = []
            
            for symbol in stocks:
                data = fetch_stock_data(symbol)
                if data and 'historical_prices' in data and len(data['historical_prices']) > 1:
                    current = data['historical_prices'][-1]
                    previous = data['historical_prices'][-2]
                    if previous > 0:  # Avoid division by zero
                        change_pct = ((current - previous) / previous) * 100
                        prices_change.append(change_pct)
            
            if prices_change:
                # Average percentage change across stocks
                avg_change = sum(prices_change) / len(prices_change)
                
                # Format with proper sign and color
                change_text = f"{'+' if avg_change >= 0 else ''}{avg_change:.2f}%"
                
                # Base value is arbitrary but consistent for indices
                base_values = {
                    "NIFTY 50": 22450,
                    "SENSEX": 73850,
                    "NIFTY BANK": 48100
                }
                
                base = base_values.get(index_name, 10000)
                value = f"{base:,.2f} ({change_text})"
                
                label_widget.setText(value)
                
                # Set color based on change direction
                if avg_change >= 0:
                    label_widget.setStyleSheet("color: #00c853; font-weight: bold;")
                else:
                    label_widget.setStyleSheet("color: #ff5252; font-weight: bold;")
            else:
                # Fallback for when no data is available
                label_widget.setText(f"-- (--)") 
                label_widget.setStyleSheet("color: #e0e0e0; font-weight: bold;")
                
        except Exception as e:
            print(f"Error updating {index_name}: {e}")
            label_widget.setText(f"-- (--)") 
            label_widget.setStyleSheet("color: #e0e0e0; font-weight: bold;")
            
    def calculate_market_sentiment(self, stocks):
        """Calculate market sentiment based on prediction scores from top stocks"""
        try:
            from stock.stock_prediction import predict_stock
            
            scores = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            # Collect prediction scores from stocks
            for symbol in stocks[:20]:  # Limit to 20 stocks for performance
                prediction = predict_stock(symbol)
                if prediction and 'score' in prediction:
                    score = prediction['score']
                    scores.append(score)
                    
                    # Count the sentiment distribution
                    if score > 0.15:
                        positive_count += 1
                    elif score < -0.15:
                        negative_count += 1
                    else:
                        neutral_count += 1
            
            if not scores:
                sentiment = 50  # Default neutral if no scores available
            else:
                # Convert average score from [-1,1] range to [0,100] range
                avg_score = sum(scores) / len(scores)
                sentiment = int((avg_score + 1) * 50)  # Convert [-1,1] to [0,100]
            
            # Update UI in the main thread
            from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(self, "update_sentiment_display", 
                                    Qt.ConnectionType.QueuedConnection,
                                    Q_ARG(int, sentiment), 
                                    Q_ARG(int, positive_count),
                                    Q_ARG(int, negative_count),
                                    Q_ARG(int, neutral_count))
            
        except Exception as e:
            print(f"Error calculating market sentiment: {e}")
    
    @pyqtSlot(int, int, int, int)
    def update_sentiment_display(self, sentiment, positive, negative, neutral):
        """Update the sentiment display (called from main thread)"""
        try:
            # Ensure sentiment is in valid range
            sentiment = max(0, min(100, sentiment))
            self.sentiment_bar.setValue(sentiment)
            
            # Update sentiment text and color based on percentage
            if sentiment > 65:
                sentiment_text = "Strongly Bullish"
                sentiment_color = "#00c853"
            elif sentiment > 55:
                sentiment_text = "Bullish"
                sentiment_color = "#8bc34a"
            elif sentiment > 45:
                sentiment_text = "Neutral"
                sentiment_color = "#ffab40"
            elif sentiment > 35:
                sentiment_text = "Bearish"
                sentiment_color = "#ff7043"
            else:
                sentiment_text = "Strongly Bearish"
                sentiment_color = "#ff5252"
                
            self.sentiment_bar.setFormat(f"{sentiment}% {sentiment_text} ({positive}/{negative}/{neutral})")
            self.sentiment_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #2a2e39; 
                    color: #ffffff; 
                    border: 1px solid #616161; 
                    border-radius: 5px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {sentiment_color}; 
                    border-radius: 5px;
                }}
            """)
            
        except Exception as e:
            print(f"Error updating sentiment display: {e}")