from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt

from stock.ui.market_overview import MarketOverviewPage
from stock.ui.stock_detail import StockDetailPage

class StockDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Indian Stock Market Dashboard")
        self.setGeometry(100, 100, 1300, 900)
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet("""
    QWidget {
        background-color: #222831; 
        color: #eeeeee;
        font-family: Arial, Helvetica, sans-serif;
    }
    
    QLabel {
        color: #e0e0e0;
    }
    
    QLabel[title="true"] {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }
    
    QLabel[subtitle="true"] {
        font-size: 16px;
        color: #aaaaaa;
        margin-bottom: 20px;
    }
    
    QPushButton {
        background-color: #3a3f48; 
        color: #e0e0e0; 
        border-radius: 4px;
        padding: 8px 15px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #4a4f58;
    }
    
    QPushButton:pressed {
        background-color: #2a2f38;
        padding-top: 10px; /* Add this line to create visible movement */
        padding-bottom: 6px; /* Add this line to create visible movement */
    }
    
    QPushButton#buyButton {
        background-color: #00b248;
        color: white;
    }
    
    QPushButton#buyButton:hover {
        background-color: #00c853;
    }
    
    QPushButton#buyButton:pressed {
        background-color: #008a3b;
    }
    
    QPushButton#sellButton {
        background-color: #d32f2f;
        color: white;
    }
    
    QPushButton#sellButton:hover {
        background-color: #ff5252;
    }
    
    QPushButton#sellButton:pressed {
        background-color: #b71c1c;
    }
    
    QLineEdit {
        background-color: #3a3f48;
        color: #e0e0e0;
        border: 1px solid #616161;
        border-radius: 4px;
        padding: 8px;
        selection-background-color: #00b248;
    }
    
    QTableWidget {
        background-color: #2a2e39;
        alternate-background-color: #30343f;
        color: #e0e0e0;
        gridline-color: #3a3f48;
        border: 1px solid #616161;
        border-radius: 4px;
    }
    
    QTableWidget::item:selected {
        background-color: #4a6572;
    }
    
    QHeaderView::section {
        background-color: #3a3f48;
        color: #e0e0e0;
        padding: 5px;
        border: none;
    }
    
    QTabWidget::pane {
        border: 1px solid #616161;
        border-radius: 4px;
    }
    
    QTabBar::tab {
        background-color: #2a2e39;
        color: #e0e0e0;
        padding: 8px 15px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #3a3f48;
    }
    
    QTabBar::tab:hover {
        background-color: #4a4f58;
    }
    
    QProgressBar {
        border: 1px solid #616161;
        border-radius: 4px;
        text-align: center;
        background-color: #2a2e39;
    }
    
    QProgressBar::chunk {
        border-radius: 4px;
    }
    
    QFrame[cardFrame="true"] {
        background-color: #2a2e39;
        border: 1px solid #616161;
        border-radius: 8px;
        padding: 15px;
    }
""")
        
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
    
    def load_stock_details(self, symbol):
        self.show_stock_details(symbol)