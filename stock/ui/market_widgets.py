from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
import random

class MarketSummaryWidget(QFrame):
    def __init__(self, parent=None):
        super(MarketSummaryWidget, self).__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("background-color: #2a2e39; border: 1px solid #616161; border-radius: 5px;")
        
        self.init_ui()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_summary)
        self.update_timer.start(60000)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Market Summary")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        layout.addWidget(title)
        
        indices_grid = QGridLayout()
        
        self.nifty_label = QLabel("NIFTY 50:")
        self.nifty_label.setStyleSheet("color: #e0e0e0;")
        self.nifty_value = QLabel("--")
        self.nifty_value.setStyleSheet("color: #e0e0e0;")
        
        self.sensex_label = QLabel("SENSEX:")
        self.sensex_label.setStyleSheet("color: #e0e0e0;")
        self.sensex_value = QLabel("--")
        self.sensex_value.setStyleSheet("color: #e0e0e0;")
        
        self.nifty_bank_label = QLabel("NIFTY BANK:")
        self.nifty_bank_label.setStyleSheet("color: #e0e0e0;")
        self.nifty_bank_value = QLabel("--")
        self.nifty_bank_value.setStyleSheet("color: #e0e0e0;")
        
        self.market_status = QLabel("Market Status: Open")
        self.market_status.setStyleSheet("color: #e0e0e0;")
        
        indices_grid.addWidget(self.nifty_label, 0, 0)
        indices_grid.addWidget(self.nifty_value, 0, 1)
        indices_grid.addWidget(self.sensex_label, 1, 0)
        indices_grid.addWidget(self.sensex_value, 1, 1)
        indices_grid.addWidget(self.nifty_bank_label, 2, 0)
        indices_grid.addWidget(self.nifty_bank_value, 2, 1)
        indices_grid.addWidget(self.market_status, 3, 0, 1, 2)
        
        layout.addLayout(indices_grid)
        
        sentiment_layout = QHBoxLayout()
        sentiment_label = QLabel("Market Sentiment:")
        sentiment_label.setStyleSheet("color: #e0e0e0;")
        
        self.sentiment_bar = QProgressBar()
        self.sentiment_bar.setRange(0, 100)
        self.sentiment_bar.setValue(50)
        self.sentiment_bar.setTextVisible(True)
        self.sentiment_bar.setFormat("%p% Bullish")
        self.sentiment_bar.setStyleSheet("background-color: #2a2e39; color: #e0e0e0;")
        
        sentiment_layout.addWidget(sentiment_label)
        sentiment_layout.addWidget(self.sentiment_bar)
        
        layout.addLayout(sentiment_layout)
        
        self.last_updated = QLabel("Last updated: --")
        self.last_updated.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(self.last_updated, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        self.update_summary()
        
    def update_summary(self):
        try:
            nifty_change = random.uniform(-1.5, 2.0)
            sensex_change = random.uniform(-1.2, 1.8)
            bank_change = random.uniform(-1.8, 2.2)
            
            self.nifty_value.setText(f"22,456.80 ({nifty_change:+.2f}%)")
            self.nifty_value.setStyleSheet(f"color: {'#00c853' if nifty_change >= 0 else '#ff5252'}; font-weight: bold;")
            
            self.sensex_value.setText(f"73,876.90 ({sensex_change:+.2f}%)")
            self.sensex_value.setStyleSheet(f"color: {'#00c853' if sensex_change >= 0 else '#ff5252'}; font-weight: bold;")
            
            self.nifty_bank_value.setText(f"48,123.45 ({bank_change:+.2f}%)")
            self.nifty_bank_value.setStyleSheet(f"color: {'#00c853' if bank_change >= 0 else '#ff5252'}; font-weight: bold;")
            
            now = datetime.now()
            if now.weekday() < 5 and 9 <= now.hour < 15 or (now.hour == 15 and now.minute < 30):
                self.market_status.setText("Market Status: Open")
                self.market_status.setStyleSheet("color: #00c853;")
            else:
                self.market_status.setText("Market Status: Closed")
                self.market_status.setStyleSheet("color: #ff5252;")
            
            sentiment = 50 + int((nifty_change + sensex_change + bank_change) * 10)
            sentiment = max(0, min(100, sentiment))
            self.sentiment_bar.setValue(sentiment)
            
            self.last_updated.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error updating market summary: {e}")