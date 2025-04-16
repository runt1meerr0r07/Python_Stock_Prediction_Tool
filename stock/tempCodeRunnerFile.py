import sys
import os
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib
matplotlib.use('QtAgg')  
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import style, cm
import matplotlib.pyplot as plt
import mplfinance as mpf

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                           QHBoxLayout, QPushButton, QTabWidget, QFrame, 
                           QGridLayout, QTableWidget, QLineEdit, QTableWidgetItem,
                           QHeaderView, QStyledItemDelegate, QScrollArea, QSplitter,
                           QStackedWidget, QComboBox, QProgressBar, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QEventLoop
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QLinearGradient, QBrush, QPalette, QGradient

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
        self.fig.tight_layout(pad=2.0)
        self.price_tracker = None
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        
    def plot_stock_data(self, prices, dates, symbol, currency="₹"):
        self.axes.clear()
        x = np.arange(len(prices))
        self.prices = prices
        self.dates = dates
        self.currency = currency
        
        if prices[-1] >= prices[0]:
            line_color = '#00c853'
            fill_color = '#00c85320'  
            accent_color = '#00952d'
        else:
            line_color = '#ff5252'
            fill_color = '#ff525220'
            accent_color = '#c50e29'
        
        self.axes.plot(x, prices, linewidth=2.5, color=line_color, zorder=3)
        self.axes.fill_between(x, prices, min(prices), alpha=0.2, color=fill_color, zorder=2)
        
        self.axes.grid(True, linestyle='--', alpha=0.15, color='#e0e0e0', zorder=1)
        self.axes.set_facecolor('#2a2e39')
        
        date_range = (dates[-1] - dates[0]).days if isinstance(dates[0], datetime) else len(dates)
        
        if date_range > 365:
            num_ticks = 6
        elif date_range > 180:
            num_ticks = 5
        else:
            num_ticks = 4
            
        tick_indices = [int(i * (len(prices)-1) / (num_ticks-1)) for i in range(num_ticks)]
        
        self.axes.set_xticks(tick_indices)
        
        date_labels = []
        for idx in tick_indices:
            if idx < len(dates):
                date_obj = dates[idx]
                if isinstance(date_obj, str):
                    try:
                        date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
                    except:
                        pass
                
                if isinstance(date_obj, datetime):
                    if date_range > 365:
                        date_labels.append(date_obj.strftime('%b %Y'))
                    else:
                        date_labels.append(date_obj.strftime('%b %d'))
                else:
                    date_labels.append(str(date_obj))
            else:
                date_labels.append("")
        
        self.axes.set_xticklabels(date_labels, color='#e0e0e0', rotation=0, fontsize=9)
        self.axes.tick_params(axis='x', pad=8)
        self.axes.tick_params(axis='y', colors='#e0e0e0', labelsize=9)
        
        y_min, y_max = min(prices), max(prices)
        y_padding = (y_max - y_min) * 0.05
        self.axes.set_ylim(y_min - y_padding, y_max + y_padding)
        
        self.axes.set_title(f"{symbol} Price History", 
                          fontweight='bold', color='#e0e0e0', 
                          fontsize=12, pad=10)
        
        if prices[-1] > prices[0]:
            trend_color = '#4caf50' 
            trend_text = "▲"
            change_pct = ((prices[-1] - prices[0]) / prices[0]) * 100
            trend_label = f"+{change_pct:.2f}%"
        else:
            trend_color = '#f44336'  
            trend_text = "▼"
            change_pct = ((prices[0] - prices[-1]) / prices[0]) * 100
            trend_label = f"-{change_pct:.2f}%"
            
        start_date = dates[0]
        end_date = dates[-1]
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except:
                pass
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except:
                pass
        
        if date_range > 365:
            start_date_str = start_date.strftime('%b %Y') if isinstance(start_date, datetime) else str(start_date)
            end_date_str = end_date.strftime('%b %Y') if isinstance(end_date, datetime) else str(end_date)
        else:
            start_date_str = start_date.strftime('%b %d') if isinstance(start_date, datetime) else str(start_date)
            end_date_str = end_date.strftime('%b %d') if isinstance(end_date, datetime) else str(end_date)
            
        self.axes.plot(0, prices[0], 'o', markersize=5, color=accent_color, zorder=4)
        self.axes.plot(len(prices)-1, prices[-1], 'o', markersize=5, color=accent_color, zorder=4)
        
        self.axes.text(0.03, 0.97, 
                     f"{trend_text} {trend_label}",
                     transform=self.axes.transAxes,
                     fontsize=10, color=trend_color, fontweight='bold',
                     verticalalignment='top', horizontalalignment='left',
                     bbox=dict(boxstyle="round,pad=0.3", fc='#2a2e39', ec=trend_color, alpha=0.7))
        
        self.axes.text(0.97, 0.97, 
                     f"High: {currency}{max(prices):.2f}\nLow: {currency}{min(prices):.2f}",
                     transform=self.axes.transAxes,
                     fontsize=9, color='#e0e0e0',
                     verticalalignment='top', horizontalalignment='right',
                     bbox=dict(boxstyle="round,pad=0.3", fc='#2a2e39', ec='#616161', alpha=0.7))
        
        for spine in self.axes.spines.values():
            spine.set_visible(False)
        
        self.price_tracker = self.axes.axvline(x=0, color='#bbbbbb', linestyle='--', alpha=0, lw=1)
        self.price_label = self.axes.text(0, 0, "", 
                                        bbox=dict(boxstyle="round,pad=0.3", fc='#2a2e39', ec="gray", alpha=0.9),
                                        color='#e0e0e0', fontsize=9, ha='center')
        self.price_label.set_visible(False)
        
        self.draw()
        
    def on_mouse_move(self, event):
        if event.inaxes != self.axes or not hasattr(self, 'prices') or not hasattr(self, 'dates') or self.price_tracker is None:
            if self.price_tracker and self.price_tracker.get_alpha() > 0:
                self.price_tracker.set_alpha(0)
                self.price_label.set_visible(False)
                self.draw_idle()
            return
        
        x_val = int(round(event.xdata))
        if x_val < 0 or x_val >= len(self.prices):
            return
            
        self.price_tracker.set_xdata([x_val, x_val])
        self.price_tracker.set_alpha(0.4)
        
        price = self.prices[x_val]
        
        date = self.dates[x_val]
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d')
            except:
                pass
        
        date_str = date.strftime('%b %d, %Y') if isinstance(date, datetime) else str(date)
        
        self.price_label.set_text(f"{date_str}\n{self.currency}{price:.2f}")
        
        x_pos = x_val
        y_pos = price
        x_bounds = self.axes.get_xlim()
        width = x_bounds[1] - x_bounds[0]
        
        if x_val < width * 0.1:
            self.price_label.set_horizontalalignment('left')
        elif x_val > width * 0.9:
            self.price_label.set_horizontalalignment('right')
        else:
            self.price_label.set_horizontalalignment('center')
            
        self.price_label.set_position((x_pos, y_pos))
        self.price_label.set_visible(True)
        
        self.draw_idle()


class InfoCard(QFrame):
    def __init__(self, title, value="--", parent=None, icon=None, color=None):
        super(InfoCard, self).__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet()
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color:
        
        header_layout.addWidget(self.title_label)
        
        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(icon).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio))
            header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        self.value_label = QLabel(value)
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
        else:
            self.value_label.setStyleSheet("color:
        
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.value_label)
        self.setLayout(layout)
        
        self.setGraphicsEffect(None)
        
    def update_value(self, value, color=None):
        self.value_label.setText(str(value))
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")


class MarketSummaryWidget(QFrame):
    def __init__(self, parent=None):
        super(MarketSummaryWidget, self).__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet()
        
        self.init_ui()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_summary)
        self.update_timer.start(60000)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Market Summary")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color:
        layout.addWidget(title)
        
        indices_grid = QGridLayout()
        
        self.nifty_label = QLabel("NIFTY 50:")
        self.nifty_label.setStyleSheet("color:
        self.nifty_value = QLabel("--")
        self.nifty_value.setStyleSheet("color:
        
        self.sensex_label = QLabel("SENSEX:")
        self.sensex_label.setStyleSheet("color:
        self.sensex_value = QLabel("--")
        self.sensex_value.setStyleSheet("color:
        
        self.nifty_bank_label = QLabel("NIFTY BANK:")
        self.nifty_bank_label.setStyleSheet("color:
        self.nifty_bank_value = QLabel("--")
        self.nifty_bank_value.setStyleSheet("color:
        
        self.market_status = QLabel("Market Status: Open")
        self.market_status.setStyleSheet("color:
        
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
        sentiment_label.setStyleSheet("color:
        
        self.sentiment_bar = QProgressBar()
        self.sentiment_bar.setRange(0, 100)
        self.sentiment_bar.setValue(50)
        self.sentiment_bar.setTextVisible(True)
        self.sentiment_bar.setFormat("%p% Bullish")
        self.sentiment_bar.setStyleSheet()
        
        sentiment_layout.addWidget(sentiment_label)
        sentiment_layout.addWidget(self.sentiment_bar)
        
        layout.addLayout(sentiment_layout)
        
        self.last_updated = QLabel("Last updated: --")
        self.last_updated.setStyleSheet("color:
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
                self.market_status.setStyleSheet("color:
            else:
                self.market_status.setText("Market Status: Closed")
                self.market_status.setStyleSheet("color:
            
            sentiment = 50 + int((nifty_change + sensex_change + bank_change) * 10)
            sentiment = max(0, min(100, sentiment))
            self.sentiment_bar.setValue(sentiment)
            
            self.last_updated.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error updating market summary: {e}")


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
        self.back_button.setStyleSheet()
        
        self.stock_header = QLabel("Select a stock to view details")
        self.stock_header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px 0; color:
        
        header_layout.addWidget(self.back_button)
        header_layout.addWidget(self.stock_header)
        header_layout.addStretch()
        
        from stock.db_manager import db
        user_balance = db.get_user_balance()
        self.balance_display = QLabel(f"Account: ₹{user_balance:,.2f}")
        self.balance_display.setStyleSheet("color:
        header_layout.addWidget(self.balance_display)
        
        main_layout.addLayout(header_layout)
        
        price_row_layout = QHBoxLayout()
        
        price_change_layout = QVBoxLayout()
        
        self.price_label = QLabel(f"{self.currency}--")
        self.price_label.setStyleSheet("font-size: 36px; font-weight: bold; color:
        self.change_label = QLabel("--")
        self.change_label.setStyleSheet("font-size: 18px; color:
        
        price_change_layout.addWidget(self.price_label)
        price_change_layout.addWidget(self.change_label)
        
        price_row_layout.addLayout(price_change_layout)
        price_row_layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        
        self.buy_button = QPushButton("Buy Stock")
        self.buy_button.setStyleSheet()
        self.buy_button.clicked.connect(self.buy_stock)
        
        self.sell_button = QPushButton("Sell Stock")
        self.sell_button.setStyleSheet()
        self.sell_button.clicked.connect(self.sell_stock)
        
        buttons_layout.addWidget(self.buy_button)
        buttons_layout.addWidget(self.sell_button)
        
        price_row_layout.addLayout(buttons_layout)
        
        main_layout.addLayout(price_row_layout)
        
        chart_selector_layout = QHBoxLayout()
        
        self.period_selector = QComboBox()
        self.period_selector.addItems(["1 Month", "3 Months", "6 Months", "1 Year", "5 Years"])
        self.period_selector.setStyleSheet()
        self.period_selector.currentIndexChanged.connect(self.update_chart_period)
        
        chart_selector_layout.addWidget(QLabel("Time Period:"))
        chart_selector_layout.addWidget(self.period_selector)
        chart_selector_layout.addStretch()
        
        self.holdings_label = QLabel()
        self.holdings_label.setStyleSheet()
        self.update_holdings_info()
        chart_selector_layout.addWidget(self.holdings_label)
        
        main_layout.addLayout(chart_selector_layout)
        
        self.chart = StockChart(self, width=10, height=6)
        main_layout.addWidget(self.chart)
        
        metrics_title = QLabel("Key Metrics")
        metrics_title.setStyleSheet("font-size: 18px; font-weight: bold; color:
        main_layout.addWidget(metrics_title)
        
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
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
        
        main_layout.addLayout(cards_layout)
        
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
                self.holdings_label.setVisible(True)
            else:
                self.holdings_label.setText("You don't own this stock")
                self.holdings_label.setVisible(True)
                
        except Exception as e:
            print(f"Error updating holdings info: {e}")
            self.holdings_label.setVisible(False)
            
    def update_chart_period(self, index):
        if self.symbol:
            self.update_stock_data()
            
    def buy_stock(self):
        if self.symbol and self.current_price > 0:
            success = TransactionDialog.show_dialog(self, self.symbol, self.current_price, "buy")
            if success:
                from stock.db_manager import db
                self.balance_display.setText(f"Account: ₹{db.get_user_balance():,.2f}")
                self.update_holdings_info()
    
    def sell_stock(self):
        if self.symbol and self.current_price > 0:
            success = TransactionDialog.show_dialog(self, self.symbol, self.current_price, "sell")
            if success:
                from stock.db_manager import db
                self.balance_display.setText(f"Account: ₹{db.get_user_balance():,.2f}")
                self.update_holdings_info()
    
    def load_stock(self, symbol):
        self.symbol = symbol
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
        if not self.symbol:
            return
            
        try:
            periods = ["1mo", "3mo", "6mo", "1y", "5y"]
            selected_period = periods[self.period_selector.currentIndex()]
            
            data = fetch_stock_data(self.symbol, period=selected_period)
            prediction = predict_stock(self.symbol)
            
            if data:
                self.currency = data.get('currency', '₹')
                
                self.current_price = data['price']
                self.stock_header.setText(f"{self.symbol} Stock Details")
                self.price_label.setText(f"{self.currency}{self.current_price}")
                
                hist_prices = data["historical_prices"]
                hist_dates = data["historical_dates"]
                
                self.update_holdings_info()
                
                if len(hist_prices) > 1:
                    period_start_price = hist_prices[0]
                    change = self.current_price - period_start_price
                    change_percent = (change / period_start_price) * 100
                    
                    period_text = ""
                    if selected_period == "1mo":
                        period_text = "1 Month"
                    elif selected_period == "3mo":
                        period_text = "3 Months"
                    elif selected_period == "6mo":
                        period_text = "6 Months"
                    elif selected_period == "1y":
                        period_text = "1 Year"
                    elif selected_period == "5y":
                        period_text = "5 Years"
                    
                    change_text = f"{change:+.2f} ({change_percent:+.2f}%) {period_text}"
                    
                    if change >= 0:
                        self.change_label.setStyleSheet("color:
                    else:
                        self.change_label.setStyleSheet("color:
                    
                    self.change_label.setText(change_text)
                
                self.rsi_card.update_value(f"{data['rsi']:.1f}", 
                                          "#ff5252" if data["rsi"] > 70 else 
                                          "#00c853" if data["rsi"] < 30 else "#e0e0e0")
                                          
                sma_20 = data['sma_20']
                sma_50 = data['sma_50']
                sma_200 = data['sma_200']
                
                if np.isnan(sma_20):
                    if len(hist_prices) >= 20:
                        sma_20 = sum(hist_prices[-20:]) / 20
                    else:
                        sma_20 = self.current_price
                self.sma20_card.update_value(f"{self.currency}{sma_20:.2f}")
                
                if np.isnan(sma_50):
                    if len(hist_prices) >= 50:
                        sma_50 = sum(hist_prices[-50:]) / 50
                    elif not np.isnan(sma_20):
                        sma_50 = sma_20
                    else:
                        sma_50 = self.current_price
                self.sma50_card.update_value(f"{self.currency}{sma_50:.2f}")
                
                if np.isnan(sma_200):
                    if len(hist_prices) >= 200:
                        sma_200 = sum(hist_prices[-200:]) / 200
                    elif not np.isnan(sma_50):
                        sma_200 = sma_50
                    else:
                        sma_200 = self.current_price
                self.sma200_card.update_value(f"{self.currency}{sma_200:.2f}")
                
                self.volume_card.update_value(self.format_large_number(data["volume"]))
                
                self.chart.plot_stock_data(hist_prices, hist_dates, self.symbol, self.currency)
            
            if prediction:
                self.prediction_card.update_value(prediction["prediction"], 
                                                "#00c853" if "Buy" in prediction["prediction"] else 
                                                "#ff5252" if "Sell" in prediction["prediction"] else "#ffab40")
                self.target_card.update_value(f"{self.currency}{prediction['target_price']}")
                
                score = prediction["score"]
                score_color = "#00c853" if score > 0.3 else "#ff5252" if score < -0.3 else "#ffab40"
                self.score_card.update_value(f"{score:+.2f}", score_color)
                
        except Exception as e:
            print(f"Error updating stock data: {e}")
            self.stock_header.setText(f"Error loading {self.symbol}")
            self.price_label.setText("--")
            self.change_label.setText(f"Could not load {self.symbol}. Please check the symbol and try again.")


class StockTableDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 2:
            text = index.data()
            if text and text.startswith("+"):
                color = QColor("#00c853")
            else:
                color = QColor("#ff5252")
                
            painter.save()
            painter.setPen(color)
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, text)
            painter.restore()
        else:
            super().paint(painter, option, index)


class MarketOverviewPage(QWidget):
    stock_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        self.nifty_stocks = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS",
            "KOTAKBANK.NS", "AXISBANK.NS", "LT.NS", "MARUTI.NS", "TATASTEEL.NS"
        ]
        
        self.gainers = []
        self.losers = []
        
        self.load_market_data()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_market_data)
        self.timer.start(300000)
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        
        title_layout = QVBoxLayout()
        main_title = QLabel("Stock Market Dashboard")
        main_title.setStyleSheet("font-size: 24px; font-weight: bold; color:
        sub_title = QLabel("Track, analyze and predict market movements")
        sub_title.setStyleSheet("font-size: 14px; color:
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(sub_title)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search stock symbol (e.g., RELIANCE, TCS)")
        self.search_input.setMinimumWidth(300)
        self.search_input.setStyleSheet()
        
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet()
        self.search_button.clicked.connect(self.search_stock)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        header_layout.addLayout(search_layout)
        
        main_layout.addLayout(header_layout)
        
        summary_row = QHBoxLayout()
        
        self.market_summary = MarketSummaryWidget()
        summary_row.addWidget(self.market_summary)
        
        quick_view_layout = QVBoxLayout()
        quick_view_label = QLabel("Quick Market View")
        quick_view_label.setStyleSheet("font-size: 16px; font-weight: bold; color:
        
        quick_view_layout.addWidget(quick_view_label)
        
        cards_layout = QHBoxLayout()
        
        self.advance_decline = InfoCard("Advance/Decline", "652 / 348")
        self.top_gainer = InfoCard("Top Gainer", "MARUTI +3.2%", color="#00c853")
        self.top_loser = InfoCard("Top Loser", "TATASTEEL -2.1%", color="#ff5252")
        
        cards_layout.addWidget(self.advance_decline)
        cards_layout.addWidget(self.top_gainer)
        cards_layout.addWidget(self.top_loser)
        
        quick_view_layout.addLayout(cards_layout)
        summary_row.addLayout(quick_view_layout)
        
        main_layout.addLayout(summary_row)
        
        tabs = QTabWidget()
        tabs.setStyleSheet()
        
        nifty_tab = QWidget()
        nifty_layout = QVBoxLayout(nifty_tab)
        
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(5)
        self.market_table.setHorizontalHeaderLabels(["Symbol", "Company", "Price", "Change", "Volume"])
        self.market_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.market_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.market_table.setStyleSheet()
        
        delegate = StockTableDelegate()
        self.market_table.setItemDelegate(delegate)
        self.market_table.itemDoubleClicked.connect(self.on_table_item_clicked)
        
        nifty_layout.addWidget(self.market_table)
        
        gainers_tab = QWidget()
        gainers_layout = QVBoxLayout(gainers_tab)
        
        self.gainers_table = QTableWidget()
        self.gainers_table.setColumnCount(5)
        self.gainers_table.setHorizontalHeaderLabels(["Symbol", "Company", "Price", "Change", "Volume"])
        self.gainers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.gainers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.gainers_table.setStyleSheet()
        
        self.gainers_table.setItemDelegate(delegate)
        self.gainers_table.itemDoubleClicked.connect(self.on_gainers_item_clicked)
        
        gainers_layout.addWidget(self.gainers_table)
        
        losers_tab = QWidget()
        losers_layout = QVBoxLayout(losers_tab)
        
        self.losers_table = QTableWidget()
        self.losers_table.setColumnCount(5)
        self.losers_table.setHorizontalHeaderLabels(["Symbol", "Company", "Price", "Change", "Volume"])
        self.losers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.losers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.losers_table.setStyleSheet()
        
        self.losers_table.setItemDelegate(delegate)
        self.losers_table.itemDoubleClicked.connect(self.on_losers_item_clicked)
        
        losers_layout.addWidget(self.losers_table)
        
        tabs.addTab(nifty_tab, "NIFTY 50 Stocks")
        tabs.addTab(gainers_tab, "Top Gainers")
        tabs.addTab(losers_tab, "Top Losers")
        
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)
    
    def load_market_data(self):
        try:
            self.market_table.setRowCount(0)
            for symbol in self.nifty_stocks:
                self.add_stock_to_table(symbol, self.market_table)
            
            stock_changes = []
            for i in range(self.market_table.rowCount()):
                symbol = self.market_table.item(i, 0).text()
                change_text = self.market_table.item(i, 3).text()
                
                try:
                    change_val = float(change_text.replace('%', '').replace('+', ''))
                    if change_text.startswith('-'):
                        change_val = -change_val
                    
                    stock_changes.append((symbol, change_val))
                except:
                    pass
            
            stock_changes.sort(key=lambda x: x[1], reverse=True)
            
            self.gainers = [s[0] for s in stock_changes[:5]]
            self.gainers_table.setRowCount(0)
            for symbol in self.gainers:
                self.add_stock_to_table(symbol, self.gainers_table)
                
            self.losers = [s[0] for s in stock_changes[-5:]]
            self.losers_table.setRowCount(0)
            for symbol in self.losers:
                self.add_stock_to_table(symbol, self.losers_table)
                
            if stock_changes:
                top_gainer = stock_changes[0]
                self.top_gainer.update_value(f"{top_gainer[0].split('.')[0]} +{top_gainer[1]:.2f}%", "#00c853")
                
                top_loser = stock_changes[-1]
                self.top_loser.update_value(f"{top_loser[0].split('.')[0]} {top_loser[1]:.2f}%", "#ff5252")
            
            self.calculate_market_sentiment()
            
        except Exception as e:
            print(f"Error loading market data: {e}")
    
    def add_stock_to_table(self, symbol, table):
        try:
            data = fetch_stock_data(symbol)
            if not data:
                return
                
            current_price = data['price']
            hist_prices = data["historical_prices"]
            
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            company_name = symbol.split('.')[0]
            
            table.setItem(row_position, 0, QTableWidgetItem(symbol))
            table.setItem(row_position, 1, QTableWidgetItem(company_name))
            table.setItem(row_position, 2, QTableWidgetItem(f"{data['currency']}{current_price:.2f}"))
            
            if len(hist_prices) > 1:
                yesterday_price = hist_prices[-2]
                change = current_price - yesterday_price
                change_percent = (change / yesterday_price) * 100
                change_text = f"{'+' if change >= 0 else ''}{change_percent:.2f}%"
                
                table.setItem(row_position, 3, QTableWidgetItem(change_text))
            else:
                table.setItem(row_position, 3, QTableWidgetItem("--"))
                
            table.setItem(row_position, 4, QTableWidgetItem(self.format_large_number(data["volume"])))
            
        except Exception as e:
            print(f"Error adding {symbol} to table: {e}")
    
    def on_table_item_clicked(self, item):
        row = item.row()
        symbol = self.market_table.item(row, 0).text()
        self.stock_selected.emit(symbol)
    
    def on_gainers_item_clicked(self, item):
        row = item.row()
        symbol = self.gainers_table.item(row, 0).text()
        self.stock_selected.emit(symbol)
    
    def on_losers_item_clicked(self, item):
        row = item.row()
        symbol = self.losers_table.item(row, 0).text()
        self.stock_selected.emit(symbol)
    
    def search_stock(self):
        symbol = self.search_input.text().strip().upper()
        if not symbol:
            return
            
        if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
            symbol = f"{symbol}.NS"
        
        try:
            original_placeholder = self.search_input.placeholderText()
            self.search_input.setPlaceholderText("Validating stock symbol...")
            self.search_input.clear()
            QApplication.processEvents()
            
            data = fetch_stock_data(symbol, validate_only=True)
            
            if data and 'valid' in data and data['valid']:
                self.stock_selected.emit(symbol)
                self.search_input.clear()
                self.search_input.setPlaceholderText(original_placeholder)
            else:
                self.search_input.setPlaceholderText(f"'{symbol}' not found. Try another symbol.")
                QTimer.singleShot(3000, lambda: self.search_input.setPlaceholderText(original_placeholder))
        
        except Exception as e:
            print(f"Error validating stock symbol: {e}")
            self.search_input.setPlaceholderText(f"Error: {str(e)[:30]}...")
            QTimer.singleShot(3000, lambda: self.search_input.setPlaceholderText(original_placeholder))
    
    def format_large_number(self, num):
        if num >= 1e9:
            return f"{num/1e9:.2f}B"
        elif num >= 1e6:
            return f"{num/1e6:.2f}M"
        elif num >= 1e3:
            return f"{num/1e3:.2f}K"
        return str(num)

    def calculate_market_sentiment(self):
        try:
            predictions = []
            
            for i in range(self.market_table.rowCount()):
                symbol = self.market_table.item(i, 0).text()
                prediction_data = predict_stock(symbol)
                
                if prediction_data:
                    predictions.append(prediction_data["score"])
            
            if not predictions:
                return 50
                
            avg_score = sum(predictions) / len(predictions)
            
            sentiment_percent = int((avg_score + 1) * 50)
            
            bullish_count = sum(1 for score in predictions if score > 0.15)
            bearish_count = sum(1 for score in predictions if score < -0.15)
            neutral_count = len(predictions) - bullish_count - bearish_count
            
            if hasattr(self, 'market_summary') and hasattr(self.market_summary, 'sentiment_bar'):
                self.market_summary.sentiment_bar.setValue(sentiment_percent)
                
                if sentiment_percent > 65:
                    sentiment_text = "Strongly Bullish"
                    sentiment_color = "#00c853"
                elif sentiment_percent > 55:
                    sentiment_text = "Bullish"
                    sentiment_color = "#8bc34a"
                elif sentiment_percent > 45:
                    sentiment_text = "Neutral"
                    sentiment_color = "#ffab40"
                elif sentiment_percent > 35:
                    sentiment_text = "Bearish"
                    sentiment_color = "#ff7043"
                else:
                    sentiment_text = "Strongly Bearish"
                    sentiment_color = "#ff5252"
                    
                self.market_summary.sentiment_bar.setFormat(
                    f"{sentiment_percent}% {sentiment_text} ({bullish_count}/{bearish_count}/{neutral_count})"
                )
                
                self.market_summary.sentiment_bar.setStyleSheet(f)
                
                self.advance_decline.update_value(f"{bullish_count} / {bearish_count} / {neutral_count}")
                
            return sentiment_percent
            
        except Exception as e:
            print(f"Error calculating market sentiment: {e}")
            return 50


class StockDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Indian Stock Market Dashboard")
        self.setGeometry(100, 100, 1300, 900)
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet()
        
        main_layout = QVBoxLayout()
        
        self.stack = QStackedWidget()
        
        self.market_page = MarketOverviewPage()
        self.stack.addWidget(self.market_page)
        
        self.stock_page = StockDetailPage()
        self.stack.addWidget(self.stock_page)
        
        self.market_page.stock_selected.connect(self.show_stock_details)
        self.stock_page.back_button.clicked.connect(self.show_market_overview)
        
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
    
    def show_stock_details(self, symbol):
        self.stock_page.load_stock(symbol)
        self.stack.setCurrentWidget(self.stock_page)
    
    def show_market_overview(self):
        self.stack.setCurrentWidget(self.market_page)


class TransactionDialog(QWidget):
    def __init__(self, parent=None, stock_symbol="", stock_price=0, action="buy"):
        super().__init__(parent, Qt.WindowType.Window)
        
        self.stock_symbol = stock_symbol
        self.stock_price = stock_price
        self.action = action
        self.quantity = 1
        self.result = False
        
        from stock.db_manager import db
        self.user_balance = db.get_user_balance()
        
        if action == "buy":
            self.setWindowTitle(f"Buy {stock_symbol}")
        else:
            self.setWindowTitle(f"Sell {stock_symbol}")
            
        self.setFixedSize(400, 500)
        self.setStyleSheet()
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        if self.action == "buy":
            icon_label = QLabel()
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "buy_icon.png")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("🛒")
                icon_label.setStyleSheet("font-size: 48px; color:
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(icon_label)
        else:
            icon_label = QLabel()
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "sell_icon.png")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("💸")
                icon_label.setStyleSheet("font-size: 48px; color:
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(icon_label)
            
        title_label = QLabel(f"{'Buy' if self.action == 'buy' else 'Sell'} {self.stock_symbol}")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        price_label = QLabel("Current Price:")
        price_label.setStyleSheet("color:
        
        price_value = QLabel(f"₹{self.stock_price:.2f}")
        price_value.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        form_layout.addWidget(price_label, 0, 0)
        form_layout.addWidget(price_value, 0, 1)
        
        qty_label = QLabel("Quantity:")
        qty_label.setStyleSheet("color:
        
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(10000)
        self.qty_spin.setValue(1)
        self.qty_spin.setStyleSheet("font-size: 18px;")
        self.qty_spin.valueChanged.connect(self.update_total)
        
        form_layout.addWidget(qty_label, 1, 0)
        form_layout.addWidget(self.qty_spin, 1, 1)
        
        total_label = QLabel("Total Cost:")
        total_label.setStyleSheet("color:
        
        self.total_value = QLabel(f"₹{self.stock_price:.2f}")
        self.total_value.setStyleSheet("font-size: 22px; font-weight: bold; color:
        
        form_layout.addWidget(total_label, 2, 0)
        form_layout.addWidget(self.total_value, 2, 1)
        
        balance_label = QLabel("Available Balance:")
        balance_label.setStyleSheet("color:
        
        self.balance_value = QLabel(f"₹{self.user_balance:.2f}")
        self.balance_value.setStyleSheet("font-size: 16px; color:
        
        form_layout.addWidget(balance_label, 3, 0)
        form_layout.addWidget(self.balance_value, 3, 1)
        
        main_layout.addLayout(form_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color:
        main_layout.addWidget(separator)
        
        info_text = ""
        if self.action == "buy":
            max_qty = int(self.user_balance / self.stock_price)
            info_text = f"You can buy up to {max_qty} shares with your current balance."
        else:
            info_text = "Selling shares will credit your account immediately."
            
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color:
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        
        confirm_text = "Buy Now" if self.action == "buy" else "Sell Now"
        self.confirm_button = QPushButton(confirm_text)
        self.confirm_button.clicked.connect(self.accept)
        if self.action == "buy":
            self.confirm_button.setStyleSheet("background-color:
        else:
            self.confirm_button.setStyleSheet("background-color:
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.confirm_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def update_total(self):
        
        self.quantity = self.qty_spin.value()
        total = self.quantity * self.stock_price
        self.total_value.setText(f"₹{total:.2f}")
        
        if self.action == "buy" and total > self.user_balance:
            self.total_value.setStyleSheet("font-size: 22px; font-weight: bold; color:
            self.confirm_button.setEnabled(False)
        else:
            color = "#00c853" if self.action == "buy" else "#ff5252"
            self.total_value.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
            self.confirm_button.setEnabled(True)
        
    def accept(self):
        
        from stock.db_manager import db
        
        if self.action == "buy":
            total_cost = self.quantity * self.stock_price
            if total_cost > self.user_balance:
                return
                
            new_balance = self.user_balance - total_cost
            db.update_user_balance(1, new_balance)
            
            db.record_transaction(1, self.stock_symbol, "buy", self.quantity, self.stock_price)
            
            print(f"Successfully bought {self.quantity} shares of {self.stock_symbol} for ₹{total_cost:.2f}")
        else:
            
            total_value = self.quantity * self.stock_price
            new_balance = self.user_balance + total_value
            db.update_user_balance(1, new_balance)
            
            db.record_transaction(1, self.stock_symbol, "sell", self.quantity, self.stock_price)
            
            print(f"Successfully sold {self.quantity} shares of {self.stock_symbol} for ₹{total_value:.2f}")
            
        self.result = True
        self.close()
        
    def reject(self):
        
        self.result = False
        self.close()
        
    @staticmethod
    def show_dialog(parent, stock_symbol, stock_price, action="buy"):
        
        dialog = TransactionDialog(parent, stock_symbol, stock_price, action)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.show()
        
        loop = QEventLoop()
        dialog.destroyed.connect(loop.quit)
        loop.exec()
        
        return dialog.result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = StockDashboard()
    window.show()
    sys.exit(app.exec())