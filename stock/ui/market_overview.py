from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTabWidget, QTableWidget, QLineEdit, QTableWidgetItem,
                           QHeaderView, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication
from stock.ui.info_card import InfoCard
from stock.ui.market_widgets import MarketSummaryWidget
from stock.ui.delegates import StockTableDelegate
from stock.models.utils import format_large_number

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
        main_title.setProperty("title", True)  # For CSS styling
        main_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff; margin-bottom: 5px;")
        main_title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        sub_title = QLabel("Track, analyze and predict market movements")
        sub_title.setProperty("subtitle", True)  # For CSS styling
        sub_title.setStyleSheet("font-size: 16px; color: #aaaaaa; margin-bottom: 15px;")
        sub_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(sub_title)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search stock symbol (e.g., RELIANCE, TCS)")
        self.search_input.setMinimumWidth(300)
        self.search_input.setStyleSheet("""
    background-color: #3a3f48; 
    color: #e0e0e0; 
    border: 1px solid #616161; 
    border-radius: 4px; 
    padding: 8px 12px;
    font-size: 14px;
""")
        self.search_input.setMinimumHeight(38)

        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("""
    background-color: #00b248; 
    color: white; 
    border-radius: 4px;
    padding: 8px 15px;
    font-weight: bold;
    font-size: 14px;
""")
        self.search_button.setObjectName("searchButton")
        self.search_button.setMinimumHeight(38)
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
        quick_view_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        
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
        tabs.setStyleSheet("background-color: #2a2e39; color: #e0e0e0;")
        
        nifty_tab = QWidget()
        nifty_layout = QVBoxLayout(nifty_tab)
        
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(5)
        self.market_table.setHorizontalHeaderLabels(["Symbol", "Company", "Price", "Change", "Volume"])
        self.market_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.market_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.market_table.setStyleSheet("background-color: #2a2e39; color: #e0e0e0;")
        
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
        self.gainers_table.setStyleSheet("background-color: #2a2e39; color: #e0e0e0;")
        
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
        self.losers_table.setStyleSheet("background-color: #2a2e39; color: #e0e0e0;")
        
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
            from stock.stockapi import fetch_stock_data
            
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
            from stock.stockapi import fetch_stock_data
            
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
                
            table.setItem(row_position, 4, QTableWidgetItem(format_large_number(data["volume"]))) 
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
            from stock.stockapi import fetch_stock_data
            from PyQt6.QtWidgets import QApplication
            
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
    
    def calculate_market_sentiment(self):
        try:
            
            bullish_count = 0
            bearish_count = 0
            neutral_count = 0
            
            
            for i in range(self.market_table.rowCount()):
                try:
                    change_text = self.market_table.item(i, 3).text()
                    if change_text.startswith('+'):
                        bullish_count += 1
                    elif change_text.startswith('-'):
                        bearish_count += 1
                    else:
                        neutral_count += 1
                except:
                    continue
                    
        
            total_stocks = bullish_count + bearish_count + neutral_count
            sentiment_percent = 50  
            if total_stocks > 0:
                sentiment_percent = int((bullish_count / total_stocks) * 100)
            
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
                
               
                self.market_summary.sentiment_bar.setStyleSheet(
                    f"QProgressBar {{ background-color: #2a2e39; border: 1px solid #616161; border-radius: 5px; text-align: center; }} "
                    f"QProgressBar::chunk {{ background-color: {sentiment_color}; border-radius: 5px; }}"
                )
                
             
                if hasattr(self, 'advance_decline'):
                    self.advance_decline.update_value(f"{bullish_count} / {bearish_count} / {neutral_count}")
            
            return sentiment_percent
            
        except Exception as e:
            print(f"Error calculating market sentiment: {e}")
            return 50  