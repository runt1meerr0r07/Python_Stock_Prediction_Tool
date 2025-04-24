import sys
import os
import threading
import subprocess
import requests
import webbrowser
import feedparser
from io import BytesIO
from PIL import Image
import yfinance as yf
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL.ImageQt import ImageQt

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QStackedLayout, QFrame, QScrollArea
)
from PyQt6.QtGui import QFont, QCursor, QPixmap
from PyQt6.QtCore import Qt, QTimer

from stock.ui.portfolio_window import PortfolioWindow  

themes = {
    "light": {
        "bg": "#ffffff", "fg": "#000000",
        "header_bg": "#eeeeee", "header_fg": "#000000",
        "button_bg": "#000000", "button_fg": "#ffffff",
        "description_fg": "#555555",
        "card_bg": "#ffffff", "card_border": "#cccccc",
        "marquee_bg": "#000000", "marquee_fg": "#ffffff"
    },
    "dark": {
        "bg": "#1e1e1e", "fg": "#ffffff",
        "header_bg": "#2b2b2b", "header_fg": "#ffffff",
        "button_bg": "#444444", "button_fg": "#ffffff",
        "description_fg": "#cccccc",
        "card_bg": "#2b2b2b", "card_border": "#444444",
        "marquee_bg": "#000000", "marquee_fg": "#ffffff"
    }
}

DEFAULT_IMAGE_URL = "https://www.publicdomainpictures.net/pictures/320000/velka/stock-market-chart.jpg"

def get_yf_rss(ticker):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(url)
    return [{"title": entry.title, "link": entry.link} for entry in feed.entries]

class NewsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.title_label = QLabel("📈 Latest Stock News")
        self.title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(self.title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.news_container = QWidget()
        self.news_layout = QVBoxLayout(self.news_container)
        self.scroll_area.setWidget(self.news_container)
        layout.addWidget(self.scroll_area)

        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_stock_news)
        self.timer.start(60000)

        self.fetch_stock_news()

    def fetch_stock_news(self):
        
        self.clear_news()
        ticker = "AAPL"
        articles = get_yf_rss(ticker)

        if not articles:
            self.news_layout.addWidget(QLabel("No news available."))
            return

        for article in articles[:10]:
            title, link = article["title"], article["link"]
            image_url = DEFAULT_IMAGE_URL
            try:
                img_data = requests.get(image_url).content
                img = Image.open(BytesIO(img_data)).resize((120, 80))
                qt_img = QPixmap.fromImage(ImageQt(img))
            except:
                qt_img = None

            frame = QFrame()
            frame.setStyleSheet("background: white; border: 1px solid #ccc; padding: 10px;")
            hbox = QHBoxLayout(frame)

            if qt_img:
                img_label = QLabel()
                img_label.setPixmap(qt_img)
                img_label.setFixedSize(120, 80)
                img_label.setScaledContents(True)
                hbox.addWidget(img_label)

            label = QLabel(title)
            label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            label.setStyleSheet("color: blue;")
            label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            label.mousePressEvent = lambda e, url=link: webbrowser.open(url)
            hbox.addWidget(label)

            self.news_layout.addWidget(frame)

    def clear_news(self):
        for i in reversed(range(self.news_layout.count())):
            widget = self.news_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

class StockAdvisorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProfitProphet Stock Advisor")
        self.setMinimumSize(1200, 800)
        self.current_theme = "dark"

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.stack = QStackedLayout()
        self.create_home_page()
        self.news_page = NewsWidget()
        self.stack.addWidget(self.news_page)

        self.create_header()
        self.main_layout.addLayout(self.stack)

        self.create_marquee()
        self.apply_theme()

    def go_home(self, event=None):
        self.stack.setCurrentWidget(self.home_page)

    def create_header(self):
        self.header = QFrame()
        self.header.setFixedHeight(70)
        self.header_layout = QHBoxLayout(self.header)

        self.app_name = QLabel("ProfitProphet Stock Advisor")
        self.app_name.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.app_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.app_name.mousePressEvent = self.go_home
        self.header_layout.addWidget(self.app_name)

        self.header_layout.addStretch()
        self.buttons = {}
        for name in ["Stock", "Portfolio", "News"]:
            btn = QPushButton(name)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFlat(True)
            btn.clicked.connect(lambda checked, n=name: self.button_clicked(n))
            self.buttons[name] = btn
            self.header_layout.addWidget(btn)

        self.toggle_btn = QPushButton("🌞 Light Mode")
        self.toggle_btn.clicked.connect(self.toggle_theme)
        self.header_layout.addWidget(self.toggle_btn)

        self.main_layout.addWidget(self.header)

    def create_home_page(self):
        self.home_page = QWidget()
        self.footer = QWidget()
        outer_layout = QVBoxLayout(self.home_page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)

        # Main center content
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(80, 60, 80, 40)
        center_layout.setSpacing(30)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title_label = QLabel("Grow Your Wealth\nThe Smart Way.")
        self.title_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.title_label)

        self.description_label = QLabel("We're revolutionizing investing with AI-driven quantitative models.")
        self.description_label.setFont(QFont("Arial", 16))
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.description_label)

        self.invest_button = QPushButton("Start Investing")
        self.invest_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.invest_button.setFixedWidth(200)
        self.invest_button.setFixedHeight(45)
        self.invest_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.invest_button.setStyleSheet("""
            QPushButton {
                background-color: #0077cc;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
            }
        """)
        center_layout.addWidget(self.invest_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Features section
        features_layout = QHBoxLayout()
        features_layout.setSpacing(40)
        features_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        features = [
            ("📊 Live Stock Data", "View current market prices, % changes, and price movement."),
            ("📈 Stock Prediction", "Analyze trends, volatility, and volume."),
            ("📰 News Updates", "Stay informed with the latest headlines."),
        ]
        for title, desc in features:
            box = self.create_feature_box(title, desc)
            features_layout.addWidget(box)

        center_layout.addLayout(features_layout)
        scroll_layout.addWidget(center_container)
        top_stocks_section = self.create_top_stocks_section()
        center_layout.addWidget(top_stocks_section)

        # Footer
        self.footer = QWidget()
        self.footer.setStyleSheet("background-color: #f0f0f0;" if self.current_theme == "light" else "background-color: #2c2c2c;")
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(40, 40, 40, 40)

        # Left side: Company name and registration details
        left_footer = QWidget()
        left_layout = QVBoxLayout(left_footer)
        left_layout.setSpacing(10)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        company_label = QLabel("ProfitProphet")
        company_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        company_label.setStyleSheet("color: #0077cc;" if self.current_theme == "light" else "color: #00aaff;")

        details_text = (
            "Registered Portfolio Manager Reg No: INP000007979\n"
            "(Validity: Apr 03, 2023 - Perpetual)\n"
            "SEBI Registered Investment Advisor Reg No: INA100015717\n"
            "(Validity: Jan 12, 2021 - Perpetual)\n"
            "SEBI Registered Research Analyst No: INH000017295\n"
            "(Validity: Jul 03, 2024 - Perpetual)\n"
            "CIN: U67100UP2019PTC123244"
        )
        details_label = QLabel(details_text)
        details_label.setFont(QFont("Arial", 10))
        details_label.setStyleSheet("color: gray;")
        details_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        details_label.setWordWrap(True)

        left_layout.addWidget(company_label)
        left_layout.addWidget(details_label)

        # Right side: Contact info
        right_footer = QWidget()
        right_layout = QVBoxLayout(right_footer)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        phone_label = QLabel("📞 +91 98765 43210")
        email_label = QLabel("✉️ info@profitprophet.in")
        address_label = QLabel("📍 42 Market Street, FinTech Tower,\nNoida, UP, India - 201301")

        for lbl in [phone_label, email_label, address_label]:
            lbl.setFont(QFont("Arial", 10))
            lbl.setStyleSheet("color: gray;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl.setWordWrap(True)

        right_layout.addWidget(phone_label)
        right_layout.addWidget(email_label)
        right_layout.addWidget(address_label)

        # Add to main footer layout
        footer_layout.addWidget(left_footer, stretch=2)
        footer_layout.addWidget(right_footer, stretch=1)

        scroll_layout.addWidget(self.footer)

        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)

        self.stack.addWidget(self.home_page)

    def create_feature_box(self, title, description):
        theme = themes[self.current_theme]

        box = QFrame()
        box.setFixedSize(320, 180)
        box.setObjectName("featureBox")

        layout = QVBoxLayout(box)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        label = QLabel(title)
        label.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        label.setObjectName("featureTitle")
        layout.addWidget(label)

        desc = QLabel(description)
        desc.setFont(QFont("Arial", 12))
        desc.setWordWrap(True)
        desc.setObjectName("featureDesc")
        layout.addWidget(desc)

        return box

    def create_top_stocks_section(self):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(25)

        tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]
        stock_changes = []

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")
                if len(hist) >= 2:
                    yesterday_close = hist["Close"].iloc[-2]
                    today_close = hist["Close"].iloc[-1]
                    pct_change = ((today_close - yesterday_close) / yesterday_close) * 100
                    stock_changes.append((ticker, pct_change, hist["Close"]))
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")

        stock_changes.sort(key=lambda x: x[1], reverse=True)
        top_3 = stock_changes[:3]
        bottom_3 = stock_changes[-3:]

        def add_section(title_text, stock_list, force_red=False):
            title = QLabel(title_text)
            title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            graph_container = QHBoxLayout()
            graph_container.setSpacing(20)

            for ticker, pct, prices in stock_list:
                graph_widget = self.create_stock_graph(ticker, pct, prices, force_red=force_red)
                graph_container.addWidget(graph_widget)

            layout.addLayout(graph_container)

        add_section("🔥 Top 3 Performing Stocks Today", top_3)
        add_section("📉 Bottom 3 Performing Stocks Today", bottom_3, force_red=True)

        return section


    def create_stock_graph(self, ticker, pct_change, prices_series, force_red=False):
        theme = themes[self.current_theme]
        text_color = theme['fg']
        grid_color = "#555555" if self.current_theme == "dark" else "#cccccc"
        bg_color = theme['card_bg']

        widget = QWidget()
        widget.setFixedHeight(200)
        v_layout = QVBoxLayout(widget)
        v_layout.setSpacing(2)
        v_layout.setContentsMargins(5, 5, 5, 5)

        # Ticker label
        title = QLabel(f"{ticker}: {pct_change:+.2f}%")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: green;" if pct_change > 0 and not force_red else "color: red;")
        v_layout.addWidget(title)

        # Chart setup
        fig = Figure(figsize=(3.5, 1.5), dpi=100, facecolor=bg_color)
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet(f"background-color: {bg_color};")
        ax = fig.add_subplot(111)

        line_color = 'red' if force_red or pct_change < 0 else 'green'

        ax.plot(prices_series.values, color=line_color, linewidth=1.8)
        ax.set_title("Price Trend", fontsize=8, color=text_color)
        ax.set_xlabel("Day", fontsize=7, color=text_color)
        ax.set_ylabel("Price", fontsize=7, color=text_color)

        ax.tick_params(axis='both', labelsize=6, colors=text_color)
        ax.spines['bottom'].set_color(text_color)
        ax.spines['left'].set_color(text_color)
        ax.spines['top'].set_color(text_color)
        ax.spines['right'].set_color(text_color)
        ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)

        fig.tight_layout(pad=1.0)
        v_layout.addWidget(canvas)

        return widget


    
    def create_marquee(self):
        self.marquee = QLabel("Stock Market Updates: ICICIBANK +3.17% | TATASE=TEEL -0.12% | SBIN +3.33%")
        self.marquee.setFixedHeight(30)
        self.marquee.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.marquee)

    def apply_theme(self):
        theme = themes[self.current_theme]
        self.central_widget.setStyleSheet(f"background-color: {theme['bg']}; color: {theme['fg']};")
        self.header.setStyleSheet(f"background-color: {theme['header_bg']};")
        self.app_name.setStyleSheet(f"color: {theme['header_fg']};")
        self.footer.setStyleSheet(f"background-color: {theme['header_bg']};")
        self.toggle_btn.setStyleSheet(f"background-color: {theme['button_bg']}; color: {theme['button_fg']};")
        self.marquee.setStyleSheet(f"background-color: {theme['marquee_bg']}; color: {theme['marquee_fg']};")
        for box in self.home_page.findChildren(QFrame, "featureBox"):
            box.setStyleSheet(f"""
                background-color: {theme['card_bg']};
                border: 2px solid {theme['card_border']};
                border-radius: 15px;
            """)
            for widget in box.findChildren(QLabel):
                if widget.objectName() == "featureTitle":
                    widget.setStyleSheet(f"color: {theme['fg']};")
                elif widget.objectName() == "featureDesc":
                    widget.setStyleSheet(f"color: {theme['description_fg']};")
        
        

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.toggle_btn.setText("🌞 Light Mode" if self.current_theme == "dark" else "🌙 Dark Mode")
        self.apply_theme()

    def button_clicked(self, name):
        if name == "Stock":
            threading.Thread(target=self.launch_stock_dashboard).start()
        elif name == "News":
            self.stack.setCurrentWidget(self.news_page)
        elif name == "Portfolio":
            print("Portfolio clicked")
            try:
                portfolio_window = PortfolioWindow()
                portfolio_window.exec()
            except Exception as e:
                print(f"Error: {e}")

    def launch_stock_dashboard(self):
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'stock', 'run_stock_dashboard.py')
            subprocess.Popen([sys.executable, script_path])
        except Exception as e:
            print(f"Error launching stock dashboard: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockAdvisorApp()
    window.showMaximized()
    sys.exit(app.exec())
