from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTabWidget, QTableWidget, QLineEdit, QTableWidgetItem,
                           QHeaderView, QGridLayout, QFrame, QApplication, QAbstractItemView)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor
from stock.ui.info_card import InfoCard
from stock.ui.market_widgets import MarketSummaryWidget
from stock.ui.delegates import StockTableDelegate
from stock.models.utils import format_large_number
from stock.stockapi import fetch_stock_data
from stock.stock_prediction import predict_stock
from stock.ui.stock_chart import StockChart

class MarketOverviewPage(QWidget):
    stock_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nifty_stocks = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS",
            "KOTAKBANK.NS", "AXISBANK.NS", "LT.NS", "MARUTI.NS", "TATASTEEL.NS"
        ]
        
        self.gainers = []
        self.losers = []
        
        # Create recommendation instances (set to None to avoid reference issues)
        self.recommendation = None
        self.risk = None
        self.advance_decline = None
        
        self.init_ui()
        
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
        
        # Add recommendations and market summary section
        indicators_section = QFrame()
        indicators_section.setStyleSheet("background-color: #2a2e39; border: 1px solid #616161; border-radius: 5px;")
        indicators_layout = QHBoxLayout(indicators_section)
        
        # Market Summary widget (left side)
        self.market_summary = MarketSummaryWidget()
        indicators_layout.addWidget(self.market_summary)
        
        # Add the recommendation panels (right side)
        self.recommendations_frame = self.create_recommendation_panels()
        indicators_layout.addWidget(self.recommendations_frame)
        
        # Set stretch factors (30% for market summary, 70% for recommendations)
        indicators_layout.setStretch(0, 3)  # Market summary takes 30%
        indicators_layout.setStretch(1, 7)  # Recommendations take 70%
        
        main_layout.addWidget(indicators_section)
        
        # Create tab widget for stock tables
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("background-color: #2a2e39; color: #e0e0e0;")
        
        # Create and add existing tabs
        self.tab_widget.addTab(self.create_stock_table("POPULAR"), "Popular Stocks")
        self.tab_widget.addTab(self.create_stock_table("GAINERS"), "Top Gainers")
        self.tab_widget.addTab(self.create_stock_table("LOSERS"), "Top Losers")
        
        # Add new tabs for recommendations
        self.tab_widget.addTab(self.create_recommendation_table("BUY"), "Top Buy Picks")
        self.tab_widget.addTab(self.create_recommendation_table("SELL"), "Top Sell Picks")
        
        main_layout.addWidget(self.tab_widget)
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
            
            # We've removed the InfoCard references, so these lines should be removed
            # or commented out since we now have recommendation panels instead
            # if stock_changes:
            #     top_gainer = stock_changes[0]
            #     self.recommendation.update_value(f"{top_gainer[0].split('.')[0]} Buy", "#00c853")
            #     
            #     top_loser = stock_changes[-1]
            #     self.risk.update_value(f"{top_loser[0].split('.')[0]} High", "#ff5252")
            
            self.calculate_market_sentiment()
            
        except Exception as e:
            print(f"Error loading market data: {e}")
            import traceback
            print(traceback.format_exc())
    
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
            # Get prediction-based sentiment from top 50 stocks
            prediction_sentiment = self.calculate_prediction_sentiment()
            
            # Get traditional price-based sentiment (bullish vs bearish count)
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
            price_sentiment_percent = 50  
            if total_stocks > 0:
                price_sentiment_percent = int((bullish_count / total_stocks) * 100)
            
            # Combine both sentiment metrics (70% prediction-based, 30% price-based)
            sentiment_percent = int((prediction_sentiment * 0.7) + (price_sentiment_percent * 0.3))
            
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
                    f"QProgressBar::chunk {{ background-color: {sentiment_color}; border-radius: 5px; }}")
            
            return sentiment_percent
            
        except Exception as e:
            print(f"Error calculating market sentiment: {e}")
            return 50
            
    def calculate_prediction_sentiment(self):
        """Calculate market sentiment based on top stocks' prediction scores"""
        try:
            # Use up to 50 top stocks from our list
            sample_stocks = self.nifty_stocks[:50]
            scores = []
            
            # Collect prediction scores
            for symbol in sample_stocks:
                data = fetch_stock_data(symbol)
                if data:
                    prediction = predict_stock(symbol)
                    if prediction and 'score' in prediction:
                        scores.append(prediction['score'])
            
            if not scores:
                return 50  # Default neutral
                
            # Convert scores to sentiment percentage
            # Scores range from -1 to 1, convert to 0-100 scale
            avg_score = sum(scores) / len(scores)
            sentiment_percent = int((avg_score + 1) * 50)  # Convert [-1,1] to [0,100]
            
            return sentiment_percent
            
        except Exception as e:
            print(f"Error calculating prediction sentiment: {e}")
            return 50

    def create_recommendation_panels(self):
        # Create the container frame for recommendations
        recommendations_frame = QFrame()
        recommendations_frame.setProperty("cardFrame", True)
        recommendations_layout = QHBoxLayout(recommendations_frame)
        
        # Buy recommendation panel
        buy_panel = QFrame()
        buy_panel.setProperty("cardFrame", True)
        buy_layout = QVBoxLayout(buy_panel)
        
        buy_header = QLabel("Top Buy Recommendation")
        buy_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00b248;")
        buy_layout.addWidget(buy_header)
        
        # Get buy recommendation
        buy_stock = self.get_top_recommendation(recommendation_type="buy")
        if buy_stock:
            symbol, data = buy_stock
            
            # Add stock details
            stock_info = QLabel(f"{symbol}: ₹{data['price']:.2f}")
            stock_info.setStyleSheet("font-size: 18px; font-weight: bold;")
            buy_layout.addWidget(stock_info)
            
            prediction_info = QLabel(f"Prediction: {data['prediction']['prediction']}")
            prediction_info.setStyleSheet("color: #00b248;")
            buy_layout.addWidget(prediction_info)
            
            target_price = QLabel(f"Target: ₹{data['prediction']['target_price']:.2f}")
            buy_layout.addWidget(target_price)
            
            # Add mini chart
            buy_chart = StockChart(width=3, height=2, dpi=80)
            buy_chart.setMinimumHeight(120)
            buy_chart.plot_stock_data(
                data['historical_prices'][-24:] if len(data['historical_prices']) >= 24 else data['historical_prices'],
                data['historical_dates'][-24:] if len(data['historical_dates']) >= 24 else data['historical_dates'],
                symbol
            )
            buy_layout.addWidget(buy_chart)
            
            # Add Buy button
            buy_button = QPushButton("Buy Now")
            buy_button.setObjectName("buyButton")
            buy_button.clicked.connect(lambda: self.stock_selected.emit(symbol))
            buy_layout.addWidget(buy_button)
        else:
            buy_layout.addWidget(QLabel("No recommendation available"))
        
        # Sell recommendation panel (similar structure)
        sell_panel = QFrame()
        sell_panel.setProperty("cardFrame", True)
        sell_layout = QVBoxLayout(sell_panel)
        
        sell_header = QLabel("Top Sell Recommendation")
        sell_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #d32f2f;")
        sell_layout.addWidget(sell_header)
        
        # Get sell recommendation
        sell_stock = self.get_top_recommendation(recommendation_type="sell")
        if sell_stock:
            symbol, data = sell_stock
            
            # Add stock details
            stock_info = QLabel(f"{symbol}: ₹{data['price']:.2f}")
            stock_info.setStyleSheet("font-size: 18px; font-weight: bold;")
            sell_layout.addWidget(stock_info)
            
            prediction_info = QLabel(f"Prediction: {data['prediction']['prediction']}")
            prediction_info.setStyleSheet("color: #d32f2f;")
            sell_layout.addWidget(prediction_info)
            
            target_price = QLabel(f"Target: ₹{data['prediction']['target_price']:.2f}")
            sell_layout.addWidget(target_price)
            
            # Add mini chart
            sell_chart = StockChart(width=3, height=2, dpi=80)
            sell_chart.setMinimumHeight(120)
            sell_chart.plot_stock_data(
                data['historical_prices'][-24:] if len(data['historical_prices']) >= 24 else data['historical_prices'],
                data['historical_dates'][-24:] if len(data['historical_dates']) >= 24 else data['historical_dates'],
                symbol
            )
            sell_layout.addWidget(sell_chart)
            
            # Add Sell button
            sell_button = QPushButton("Sell Now")
            sell_button.setObjectName("sellButton")
            sell_button.clicked.connect(lambda: self.stock_selected.emit(symbol))
            sell_layout.addWidget(sell_button)
        else:
            sell_layout.addWidget(QLabel("No recommendation available"))
        
        recommendations_layout.addWidget(buy_panel)
        recommendations_layout.addWidget(sell_panel)
        
        return recommendations_frame

    def get_top_recommendation(self, recommendation_type="buy"):
        """Get the top buy or sell recommendation"""
        try:
            # Use your top stocks list from the existing code
            stock_list = self.nifty_stocks
            
            results = []
            for symbol in stock_list[:15]:  # Check the first 15 stocks
                data = fetch_stock_data(symbol)
                if data:
                    prediction = predict_stock(symbol)
                    if prediction:
                        data['prediction'] = prediction
                        score = prediction['score']
                        
                        if recommendation_type == "buy" and score > 0.15:
                            results.append((symbol, data))
                        elif recommendation_type == "sell" and score < -0.15:
                            results.append((symbol, data))
            
            # Sort by score (absolute value for sell recommendations)
            if recommendation_type == "buy":
                results.sort(key=lambda x: x[1]['prediction']['score'], reverse=True)
            else:
                results.sort(key=lambda x: abs(x[1]['prediction']['score']), reverse=True)
            
            return results[0] if results else None
        
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return None

    def create_stock_table(self, table_type="POPULAR"):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Symbol", "Company", "Price", "Change %", "Volume"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        
        delegate = StockTableDelegate()
        table.setItemDelegate(delegate)
        
        if table_type == "POPULAR":
            self.market_table = table
            table.itemDoubleClicked.connect(self.on_table_item_clicked)
        elif table_type == "GAINERS":
            self.gainers_table = table
            table.itemDoubleClicked.connect(self.on_gainers_item_clicked)
        elif table_type == "LOSERS":
            self.losers_table = table
            table.itemDoubleClicked.connect(self.on_losers_item_clicked)
            
        return table

    def create_recommendation_table(self, table_type):
        """Create a table for buy or sell recommendations"""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Symbol", "Name", "Price", "Prediction", "Target", "Score"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        
        # Populate with recommendation data
        self.populate_recommendation_table(table, table_type)
        
        # Connect selection signal
        table.itemDoubleClicked.connect(lambda item: self.stock_selected.emit(table.item(item.row(), 0).text()))
        
        return table

    def populate_recommendation_table(self, table, table_type):
        """Populate the recommendation table with data"""
        try:
            stock_list = self.nifty_stocks
            results = []
            
            # Show loading indicator
            table.setRowCount(1)
            loading_item = QTableWidgetItem("Loading recommendations...")
            loading_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setSpan(0, 0, 1, 6)
            table.setItem(0, 0, loading_item)
            QApplication.processEvents()
            
            # Process stocks for recommendations
            for symbol in stock_list[:30]:  # Check top 30 stocks
                data = fetch_stock_data(symbol)
                if data:
                    prediction = predict_stock(symbol)
                    if prediction:
                        prediction_type = prediction['prediction']
                        score = prediction['score']
                        
                        if (table_type == "BUY" and score > 0.15) or \
                           (table_type == "SELL" and score < -0.15):
                            results.append((symbol, data, prediction))
            
            # Sort by score
            if table_type == "BUY":
                results.sort(key=lambda x: x[2]['score'], reverse=True)
            else:
                results.sort(key=lambda x: x[2]['score'])
            
            # Take top 10
            results = results[:10]
            
            # Clear loading indicator
            table.clearSpans()
            table.setRowCount(len(results))
            
            # Fill the table
            for row, (symbol, data, prediction) in enumerate(results):
                # Symbol
                symbol_item = QTableWidgetItem(symbol)
                table.setItem(row, 0, symbol_item)
                
                # Name
                name = symbol.split('.')[0]
                name_item = QTableWidgetItem(name)
                table.setItem(row, 1, name_item)
                
                # Price
                price = data.get('price', 0)
                price_item = QTableWidgetItem(f"₹{price:.2f}")
                price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(row, 2, price_item)
                
                # Prediction
                pred_item = QTableWidgetItem(prediction['prediction'])
                if "Buy" in prediction['prediction']:
                    pred_item.setForeground(QColor('#00b248'))
                elif "Sell" in prediction['prediction']:
                    pred_item.setForeground(QColor('#d32f2f'))
                table.setItem(row, 3, pred_item)
                
                # Target
                target_item = QTableWidgetItem(f"₹{prediction['target_price']:.2f}")
                target_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(row, 4, target_item)
                
                # Score
                score_item = QTableWidgetItem(f"{prediction['score']:.2f}")
                score_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if prediction['score'] > 0:
                    score_item.setForeground(QColor('#00b248'))
                else:
                    score_item.setForeground(QColor('#d32f2f'))
                table.setItem(row, 5, score_item)
        
        except Exception as e:
            table.setRowCount(1)
            error_item = QTableWidgetItem(f"Error loading recommendations: {e}")
            error_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setSpan(0, 0, 1, 6)
            table.setItem(0, 0, error_item)