from stock.ui.stock_chart import StockChart
from stock.ui.info_card import InfoCard
from stock.models.utils import safe_compare, format_large_number
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QGridLayout, QFrame, QScrollArea)  
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6 import QtWidgets
import os

class StockDetailPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.symbol = ""
        self.currency = "₹"
        self.current_price = 0
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        
        self.back_button = QPushButton("← Back to Market")
        self.back_button.setStyleSheet("background-color: #3a3f48; color: #e0e0e0; padding: 5px 10px; border-radius: 3px;")
        
        self.stock_header = QLabel("Select a stock to view details")
        self.stock_header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px 0; color: #e0e0e0;")
        
        header_layout.addWidget(self.back_button)
        header_layout.addWidget(self.stock_header)
        header_layout.addStretch()
        
        # Add favorite button
        self.favorite_button = QPushButton()
        self.favorite_button.setFixedSize(32, 32)
        self.favorite_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }
        """)
        
        # Use the correct path to star icons
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'star_empty.png')
        self.favorite_button.setIcon(QIcon(icon_path))
        self.favorite_button.setIconSize(QSize(24, 24))
        self.favorite_button.setToolTip("Add to Favorites")
        self.favorite_button.clicked.connect(self.toggle_favorite)
        header_layout.addWidget(self.favorite_button)
        
        from stock.db_manager import db
        user_balance = db.get_user_balance()
        self.balance_display = QLabel(f"Account: ₹{user_balance:,.2f}")
        self.balance_display.setStyleSheet("color: #e0e0e0;")
        header_layout.addWidget(self.balance_display)
        
        main_layout.addLayout(header_layout)
        
        price_row_layout = QHBoxLayout()
        
        price_change_layout = QHBoxLayout()  

        self.price_label = QLabel(f"{self.currency}--")
        self.price_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #e0e0e0;")
        self.change_label = QLabel("--")
        self.change_label.setStyleSheet("font-size: 18px; color: #e0e0e0; margin-left: 10px; margin-top: 10px;")

        price_change_layout.addWidget(self.price_label)
        price_change_layout.addWidget(self.change_label)
        price_change_layout.addStretch()
        
        price_row_layout.addLayout(price_change_layout)
        price_row_layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        
        self.buy_button = QPushButton("Buy Stock")
        self.buy_button.setObjectName("buyButton")
        self.buy_button.setStyleSheet("""
    background-color: #00b248; 
    color: white; 
    font-weight: bold; 
    padding: 10px 20px; 
    border-radius: 4px;
    font-size: 15px;
""")
        self.buy_button.clicked.connect(self.buy_stock)
        
        self.sell_button = QPushButton("Sell Stock")
        self.sell_button.setObjectName("sellButton")
        self.sell_button.setStyleSheet("""
    background-color: #d32f2f; 
    color: white; 
    font-weight: bold; 
    padding: 10px 20px; 
    border-radius: 4px;
    font-size: 15px;
""")
        self.sell_button.clicked.connect(self.sell_stock)
        
        buttons_layout.addWidget(self.buy_button)
        buttons_layout.addWidget(self.sell_button)
        
        price_row_layout.addLayout(buttons_layout)
        
        main_layout.addLayout(price_row_layout)
        
        chart_selector_layout = QHBoxLayout()
        
        self.period_selector = QComboBox()
        self.period_selector.addItems(["1 Month", "3 Months", "6 Months", "1 Year", "5 Years"])
        self.period_selector.setStyleSheet("""
    QComboBox {
        background-color: #3a3f48;
        color: #e0e0e0;
        border: 1px solid #616161;
        border-radius: 4px;
        padding: 5px 10px;
        min-height: 25px;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 25px;
        border-left: 1px solid #616161;
    }
    QComboBox::down-arrow {
        image: url(down_arrow.png);
        width: 14px;
        height: 14px;
    }
    /* If image doesn't load, use this fallback arrow */
    QComboBox::down-arrow:!enabled {
        border-top: 6px solid #e0e0e0;
        border-right: 4px solid transparent;
        border-left: 4px solid transparent;
        width: 0;
        height: 0;
    }
    QComboBox::down-arrow {
        border-top: 6px solid #e0e0e0;
        border-right: 4px solid transparent;
        border-left: 4px solid transparent;
        width: 0;
        height: 0;
    }
    QComboBox QAbstractItemView {
        background-color: #2a2e39;
        color: #e0e0e0;
        selection-background-color: #3a3f48;
        selection-color: #ffffff;
        border: 1px solid #616161;
    }
""")
        self.period_selector.setMinimumWidth(120)
        self.period_selector.setMaximumWidth(150)
        self.period_selector.currentIndexChanged.connect(self.update_chart_period)
        
        chart_selector_layout.addWidget(QLabel("Time Period:"))
        chart_selector_layout.addWidget(self.period_selector)
        chart_selector_layout.addStretch()
        
        self.holdings_label = QLabel()
        self.holdings_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        self.update_holdings_info()
        chart_selector_layout.addWidget(self.holdings_label)
        
        main_layout.addLayout(chart_selector_layout)
        
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(25) 

       
        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.Shape.StyledPanel)
        chart_frame.setFrameShadow(QFrame.Shadow.Raised)
        chart_frame.setStyleSheet("background-color: #2a2e39; border: 1px solid #616161; border-radius: 8px;")
        chart_frame.setMinimumHeight(400)

        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(10, 10, 10, 10)
        self.chart = StockChart(self, width=10, height=6)
        chart_layout.addWidget(self.chart)

        
        metrics_frame = QFrame()
        metrics_frame.setFrameShape(QFrame.Shape.StyledPanel)
        metrics_frame.setFrameShadow(QFrame.Shadow.Raised)
        metrics_frame.setStyleSheet("background-color: #2a2e39; border: 1px solid #616161; border-radius: 8px;")

        metrics_layout = QVBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(15, 15, 15, 15)

        metrics_title = QLabel("Key Metrics")
        metrics_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0;")
        metrics_layout.addWidget(metrics_title)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        cards_layout.setContentsMargins(0, 10, 0, 0)

        self.rsi_card = InfoCard("RSI (14)")
        self.sma20_card = InfoCard("SMA 20")
        self.sma50_card = InfoCard("SMA 50")
        self.sma200_card = InfoCard("SMA 200")
        self.volume_card = InfoCard("Volume")
        self.prediction_card = InfoCard("AI Prediction")
        self.target_card = InfoCard("Target Price")
        self.score_card = InfoCard("Confidence Score")

        cards_layout.addWidget(self.rsi_card, 0, 0)
        cards_layout.addWidget(self.sma20_card, 0, 1)
        cards_layout.addWidget(self.sma50_card, 0, 2)
        cards_layout.addWidget(self.sma200_card, 0, 3)
        cards_layout.addWidget(self.volume_card, 1, 0)
        cards_layout.addWidget(self.prediction_card, 1, 1)
        cards_layout.addWidget(self.target_card, 1, 2)
        cards_layout.addWidget(self.score_card, 1, 3)

        metrics_layout.addLayout(cards_layout)

       
        scroll_layout.addWidget(chart_frame)
        scroll_layout.addWidget(metrics_frame)
        scroll_layout.addStretch()  

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
    
    def update_holdings_info(self):
        if not self.symbol:
            self.holdings_label.setText("")
            self.holdings_label.setVisible(False)
            return
            
        try:
            from stock.db_manager import db
            holdings = db.get_user_holdings()
            
            user_shares = 0
            if holdings:
                for holding in holdings:
                    if holding['stock_ticker'] == self.symbol:
                        user_shares = holding['shares']
                        break
            
            if user_shares > 0:
                total_value = user_shares * self.current_price
                self.holdings_label.setText(f"You own: {user_shares} shares (₹{total_value:,.2f})")
                self.holdings_label.setStyleSheet("color: #00c853; font-weight: bold;")
            else:
                self.holdings_label.setText("You don't own this stock")
                self.holdings_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
                
            self.holdings_label.setVisible(True)
            
        except Exception as e:
            print(f"Error updating holdings info: {e}")
            self.holdings_label.setText("Error checking holdings")
            self.holdings_label.setVisible(True)
    
    def update_user_balance_display(self):
        from stock.db_manager import db
        user_balance = db.get_user_balance()
        self.balance_display.setText(f"Account: ₹{user_balance:,.2f}")
    
    def update_chart_period(self, index):
        if self.symbol:
            self.update_stock_data()
            
    def buy_stock(self):
        if self.symbol and self.current_price > 0:
            from stock.ui.transaction import TransactionDialog
            success = TransactionDialog.show_dialog(self, self.symbol, self.current_price, "buy")
            if success:
                self.update_user_balance_display()
                self.update_holdings_info()
    
    def sell_stock(self):
        if self.symbol and self.current_price > 0:
            from stock.ui.transaction import TransactionDialog
            success = TransactionDialog.show_dialog(self, self.symbol, self.current_price, "sell")
            if success:
                self.update_user_balance_display()
                self.update_holdings_info()
    
    def load_stock(self, symbol):
        self.symbol = symbol
        self.update_stock_data()
        self.update_favorite_button()  # Update the favorite button icon
    
    def update_stock_data(self):
        if not self.symbol:
            return
            
        try:
            periods = ["1mo", "3mo", "6mo", "1y", "5y"]
            selected_period = periods[self.period_selector.currentIndex()]
            
            
            from stock.stockapi import fetch_stock_data
            from stock.stock_prediction import predict_stock
            
            data = fetch_stock_data(self.symbol, period=selected_period)
            
            if not data:
                self.stock_header.setText(f"Error loading {self.symbol}")
                return
                
            
            self.currency = data.get('currency', '₹')
            self.current_price = data.get('price')
            
            
            if self.current_price is None:
                self.current_price = 0.0
                
            
            self.stock_header.setText(f"{self.symbol} Stock Details")
            self.price_label.setText(f"{self.currency}{self.current_price}")
            
            hist_prices = data.get("historical_prices", [])
            hist_dates = data.get("historical_dates", [])
            
            self.update_holdings_info()
            
            if len(hist_prices) > 1:
                period_start_price = hist_prices[0]
                change = self.current_price - period_start_price
                change_percent = (change / period_start_price) * 100
                
               
                period_mapping = {
                    "1mo": "1 Month", "3mo": "3 Months", 
                    "6mo": "6 Months", "1y": "1 Year", "5y": "5 Years"
                }
                period_text = period_mapping.get(selected_period, "")
                
                change_text = f"{change:+.2f} ({change_percent:+.2f}%) {period_text}"
                
                
                if change >= 0:
                    self.change_label.setStyleSheet("color: #00c853; font-size: 18px; margin-left: 10px; margin-top: 10px;")
                else:
                    self.change_label.setStyleSheet("color: #ff5252; font-size: 18px; margin-left: 10px; margin-top: 10px;")
                
                self.change_label.setText(change_text)
            
           
            rsi_value = data.get('rsi')
            if rsi_value is None:
                rsi_value = 50.0
                
            if safe_compare(rsi_value, 70, "gt"):
                rsi_color = "#ff5252"  
            elif safe_compare(rsi_value, 30, "lt"):
                rsi_color = "#00c853"  
            else:
                rsi_color = "#e0e0e0"  
                
            self.rsi_card.update_value(f"{rsi_value:.1f}", rsi_color)
            
            sma_20 = data.get('sma_20')
            if sma_20 is None:
                sma_20 = self.current_price
                
            sma_50 = data.get('sma_50')
            if sma_50 is None:
                sma_50 = self.current_price
                
            sma_200 = data.get('sma_200')
            if sma_200 is None:
                sma_200 = self.current_price
                
            
            self.sma20_card.update_value(f"{self.currency}{sma_20:.2f}")
            self.sma50_card.update_value(f"{self.currency}{sma_50:.2f}")
            self.sma200_card.update_value(f"{self.currency}{sma_200:.2f}")
            
            volume = data.get("volume")
            if volume is None:
                volume = 0
                
            self.volume_card.update_value(format_large_number(volume))
            
            
            if hist_prices and hist_dates:
                self.chart.plot_stock_data(hist_prices, hist_dates, self.symbol, self.currency)
                
            
            prediction = predict_stock(self.symbol)
            if prediction:
                pred_text = prediction.get("prediction", "Hold")
                if pred_text is None:
                    pred_text = "Hold"
                    
                if pred_text and "Buy" in pred_text:
                    pred_color = "#00c853"
                elif pred_text and "Sell" in pred_text:
                    pred_color = "#ff5252"
                else:
                    pred_color = "#ffab40"
                    
                self.prediction_card.update_value(pred_text, pred_color)
                
                target_price = prediction.get('target_price')
                if target_price is None:
                    target_price = self.current_price
                    
                self.target_card.update_value(f"{self.currency}{target_price:.2f}")
                
                
                score = prediction.get("score", 0)
                if score is None:
                    score = 0
                    
                
                if safe_compare(score, 0.3, "gt"):
                    score_color = "#00c853"
                elif safe_compare(score, -0.3, "lt"):
                    score_color = "#ff5252"
                else:
                    score_color = "#ffab40"
                    
                self.score_card.update_value(f"{score:+.2f}", score_color)
                
        except Exception as e:
            print(f"Error updating stock data: {e}")
            import traceback
            print(traceback.format_exc())  
            self.stock_header.setText(f"Error loading {self.symbol}")
            self.price_label.setText("--")
            self.change_label.setText(f"Could not load {self.symbol}. Please check the symbol and try again.")
    
    def toggle_favorite(self):
        """Toggle the favorite status of the current stock"""
        if not self.symbol:
            return
            
        try:
            from stock.db_manager import db
            user_id = 1  # Default user ID
            
            # Check current favorite status
            is_favorite = db.is_favorite(user_id, self.symbol)
            
            if is_favorite:
                # Remove from favorites
                success = db.remove_from_favorites(user_id, self.symbol)
                if success:
                    empty_star_path = os.path.join(os.path.dirname(__file__), 'icons', 'star_empty.png')
                    self.favorite_button.setIcon(QIcon(empty_star_path))
                    self.favorite_button.setToolTip("Add to Favorites")
            else:
                # Add to favorites
                success = db.add_to_favorites(user_id, self.symbol)
                if success:
                    filled_star_path = os.path.join(os.path.dirname(__file__), 'icons', 'star_filled.png')
                    self.favorite_button.setIcon(QIcon(filled_star_path))
                    self.favorite_button.setToolTip("Remove from Favorites")
        except Exception as e:
            print(f"Error toggling favorite status: {e}")
    
    def update_favorite_button(self):
        """Update the favorite button icon based on the stock's favorite status"""
        if not self.symbol:
            return
            
        try:
            from stock.db_manager import db
            user_id = 1  # Default user ID
            
            # Check favorite status
            is_favorite = db.is_favorite(user_id, self.symbol)
            
            if is_favorite:
                filled_star_path = os.path.join(os.path.dirname(__file__), 'icons', 'star_filled.png')
                self.favorite_button.setIcon(QIcon(filled_star_path))
                self.favorite_button.setToolTip("Remove from Favorites")
            else:
                empty_star_path = os.path.join(os.path.dirname(__file__), 'icons', 'star_empty.png')
                self.favorite_button.setIcon(QIcon(empty_star_path))
                self.favorite_button.setToolTip("Add to Favorites")
        except Exception as e:
            print(f"Error updating favorite button: {e}")
            empty_star_path = os.path.join(os.path.dirname(__file__), 'icons', 'star_empty.png')
            self.favorite_button.setIcon(QIcon(empty_star_path))