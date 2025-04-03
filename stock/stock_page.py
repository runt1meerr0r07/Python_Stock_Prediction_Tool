import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib
matplotlib.use('QtAgg')  

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import style

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                           QHBoxLayout, QPushButton, QComboBox, QFrame, 
                           QGridLayout, QSplitter, QLineEdit, QCompleter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette


from stock.stockapi import fetch_stock_data
from stock.stock_prediction import predict_stock


style.use('dark_background')

class StockChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#1e222a')
        self.axes = self.fig.add_subplot(111)
        super(StockChart, self).__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()
        
    def plot_stock_data(self, prices, symbol, currency="₹"):
        self.axes.clear()
        
        
        x = np.arange(len(prices))
        
        
        if prices[-1] >= prices[0]:
            line_color = '#00c853'  
            fill_color = '#00c85330'  
        else:
            line_color = '#ff5252'  
            fill_color = '#ff525230'  
        
        
        self.axes.plot(x, prices, linewidth=2, color=line_color)
        
        
        self.axes.fill_between(x, prices, min(prices), alpha=0.2, color=fill_color)
        
        
        self.axes.grid(True, linestyle='--', alpha=0.3, color='#616161')
        self.axes.set_facecolor('#2a2e39')
        

        self.axes.set_xticks([0, len(prices)//2, len(prices)-1])
        self.axes.set_xticklabels([f"-{len(prices)} days", f"-{len(prices)//2} days", "Today"], color='#e0e0e0')
        
        
        self.axes.tick_params(axis='y', colors='#e0e0e0')
        
        
        self.axes.set_title(f"{symbol} Price History (Last {len(prices)} Days)", 
                           fontweight='bold', color='#e0e0e0', fontsize=13)
        
       
        self.axes.annotate(f"{currency}{prices[0]:.2f}", (0, prices[0]), 
                          textcoords="offset points", xytext=(-20,10), 
                          ha='right', color='#e0e0e0')
        self.axes.annotate(f"{currency}{prices[-1]:.2f}", (len(prices)-1, prices[-1]), 
                          textcoords="offset points", xytext=(20,10), 
                          ha='left', color='#e0e0e0')
        
        
        if prices[-1] > prices[0]:
            trend_color = '#4caf50' 
            trend_text = "▲"
        else:
            trend_color = '#f44336'  
            trend_text = "▼"
            
        self.axes.annotate(trend_text, (len(prices)-1, prices[-1]),
                          textcoords="offset points", xytext=(40,0), 
                          fontsize=16, color=trend_color, fontweight='bold')
        
        self.fig.tight_layout()
        self.draw()


class InfoCard(QFrame):
    def __init__(self, title, value="--", parent=None):
        super(InfoCard, self).__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                border-radius: 10px;
                background-color: #2a2e39;
                border: 1px solid #3d4456;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #9e9e9e; font-size: 12px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)
        
    def update_value(self, value, color=None):
        self.value_label.setText(str(value))
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")


class StockPage(QWidget):
    def __init__(self, symbol="RELIANCE.NS"):
        super().__init__()
        self.symbol = symbol
        self.currency = "₹"  # Default to Indian Rupee
        self.setWindowTitle(f"Indian Stock Dashboard - {self.symbol}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set the global style - Dark theme
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #1e222a;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3d5afe;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #536dfe;
            }
            QPushButton:pressed {
                background-color: #304ffe;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #3d4456;
                border-radius: 4px;
                background-color: #2a2e39;
                color: #e0e0e0;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2e39;
                color: #e0e0e0;
                selection-background-color: #3d5afe;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #3d4456;
                border-radius: 4px;
                background-color: #2a2e39;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        
        header_layout = QHBoxLayout()
        
        
        self.symbol_input = QLineEdit(self.symbol)
        self.symbol_input.setPlaceholderText("Enter stock symbol (e.g., RELIANCE.NS, TCS.NS)...")
        self.symbol_input.setMaximumWidth(250)
        
       
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.change_stock)
        
        header_layout.addWidget(QLabel("Stock Symbol:"))
        header_layout.addWidget(self.symbol_input)
        header_layout.addWidget(self.search_button)
        header_layout.addStretch()
        
        
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.update_stock_data)
        header_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(header_layout)
        
       
        self.stock_header = QLabel(f"Loading {self.symbol}...")
        self.stock_header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px 0; color: #e0e0e0;")
        main_layout.addWidget(self.stock_header)
        
        
        price_change_layout = QHBoxLayout()
        self.price_label = QLabel(f"{self.currency}--")
        self.price_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #e0e0e0;")
        self.change_label = QLabel("--")
        self.change_label.setStyleSheet("font-size: 18px; color: #9e9e9e;")
        
        price_change_layout.addWidget(self.price_label)
        price_change_layout.addWidget(self.change_label)
        price_change_layout.addStretch()
        
        main_layout.addLayout(price_change_layout)
        
        
        cards_layout = QGridLayout()
        cards_layout.setSpacing(10)
        
        self.rsi_card = InfoCard("RSI (14)")
        self.sma20_card = InfoCard("SMA 20")
        self.sma50_card = InfoCard("SMA 50")
        self.sma200_card = InfoCard("SMA 200")
        self.volume_card = InfoCard("Volume")
        self.prediction_card = InfoCard("Prediction")
        self.target_card = InfoCard("Target Price")
        self.score_card = InfoCard("Score")
        
        cards_layout.addWidget(self.rsi_card, 0, 0)
        cards_layout.addWidget(self.sma20_card, 0, 1)
        cards_layout.addWidget(self.sma50_card, 0, 2)
        cards_layout.addWidget(self.sma200_card, 0, 3)
        cards_layout.addWidget(self.volume_card, 1, 0)
        cards_layout.addWidget(self.prediction_card, 1, 1)
        cards_layout.addWidget(self.target_card, 1, 2)
        cards_layout.addWidget(self.score_card, 1, 3)
        
        main_layout.addLayout(cards_layout)
        
       
        self.chart = StockChart(self, width=10, height=6)
        main_layout.addWidget(self.chart)
        
        
        
        self.setLayout(main_layout)
        
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stock_data)
        self.timer.start(300000) 
        
        
        self.update_stock_data()
    
    def change_stock(self):
        new_symbol = self.symbol_input.text().upper()
        if new_symbol and new_symbol != self.symbol:
            if not (new_symbol.endswith('.NS') or new_symbol.endswith('.BO')):
                new_symbol = f"{new_symbol}.NS"
                
            self.symbol = new_symbol
            self.setWindowTitle(f"Indian Stock Dashboard - {self.symbol}")
            self.update_stock_data()
    
    def format_large_number(self, num):
        if num >= 1e9:
            return f"{num/1e9:.2f}B"
        elif num >= 1e6:
            return f"{num/1e6:.2f}M"
        elif num >= 1e3:
            return f"{num/1e3:.2f}K"
        return str(num)

    def update_stock_data(self):
        try:
            data = fetch_stock_data(self.symbol)
            prediction = predict_stock(self.symbol)
            
            if data:
                self.currency = data.get('currency', '₹')
                
                
                current_price = data['price']
                self.stock_header.setText(f"{self.symbol} Stock Dashboard")
                self.price_label.setText(f"{self.currency}{current_price}")
                
                hist_prices = data["historical_prices"]
                if len(hist_prices) > 1:
                    yesterday_price = hist_prices[-2]
                    change = current_price - yesterday_price
                    change_percent = (change / yesterday_price) * 100
                    change_text = f"{change:+.2f} ({change_percent:+.2f}%)"
                    
                    if change >= 0:
                        self.change_label.setStyleSheet("color: #00c853; font-size: 18px;")
                    else:
                        self.change_label.setStyleSheet("color: #ff5252; font-size: 18px;")
                    
                    self.change_label.setText(change_text)
                
                
                self.rsi_card.update_value(data["rsi"], "#ff5252" if data["rsi"] > 70 else "#00c853" if data["rsi"] < 30 else "#e0e0e0")
                self.sma20_card.update_value(f"{self.currency}{data['sma_20']:.2f}")
                self.sma50_card.update_value(f"{self.currency}{data['sma_50']:.2f}")
                self.sma200_card.update_value(f"{self.currency}{data['sma_200']:.2f}")
                self.volume_card.update_value(self.format_large_number(data["volume"]))
                
                
                self.chart.plot_stock_data(hist_prices, self.symbol, self.currency)
            
            if prediction:
                self.prediction_card.update_value(prediction["prediction"], 
                                                "#00c853" if "Buy" in prediction["prediction"] else 
                                                "#ff5252" if "Sell" in prediction["prediction"] else "#ffab40")
                self.target_card.update_value(f"{self.currency}{prediction['target_price']}")
                
                score = prediction["score"]
                score_color = "#00c853" if score > 0.3 else "#ff5252" if score < -0.3 else "#ffab40"
                self.score_card.update_value(score, score_color)
                
        except Exception as e:
            print(f"Error updating stock data: {e}")
            self.stock_header.setText(f"Error loading {self.symbol}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
   
    app.setStyle("Fusion")
    
    window = StockPage("RELIANCE.NS")  
    window.show()
    sys.exit(app.exec())
