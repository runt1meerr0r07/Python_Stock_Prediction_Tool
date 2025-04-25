from PyQt6 import QtWidgets, QtCore
import requests


class NewsWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock News")
        self.resize(1000, 720)
        self.setStyleSheet("background-color: #121212; color: white; font-size: 14px;")
        self.showMaximized()
        main_layout = QtWidgets.QVBoxLayout(self)

        # Top bar
        top_bar = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search News...")
        search_btn = QtWidgets.QPushButton("Search")
        search_btn.clicked.connect(self.fetch_and_display_news)

        home_btn = QtWidgets.QPushButton("Home")
        home_btn.setFixedHeight(40)  # Make Home button bigger
        home_btn.setFixedWidth(100)
        home_btn.clicked.connect(self.go_home)

        top_bar.addWidget(self.search_input)
        top_bar.addWidget(search_btn)
        top_bar.addStretch()
        top_bar.addWidget(home_btn)

        main_layout.addLayout(top_bar)

        # Scroll area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        main_layout.addWidget(self.scroll_area)

        # Categories
        self.CATEGORIES = {
            "MARKET UPDATES": ["market", "index", "indices", "nifty", "sensex", "dow", "nasdaq", "bse"],
            "INVESTING": ["investment", "investor", "portfolio", "mutual fund", "etf"],
            "COMPANY NEWS": ["earnings", "revenue", "profit", "loss", "acquisition", "merger"],
            "REGULATIONS": ["rbi", "sebi", "regulation", "policy", "interest rate"],
            "ECONOMY": ["gdp", "inflation", "economy", "economic", "budget", "fiscal"],
            "CRYPTO": ["bitcoin", "crypto", "blockchain", "ethereum"],
            "BANKING": ["bank", "loan", "credit", "finance", "nbfc"]
        }

        self.fetch_and_display_news()

    def fetch_and_display_news(self):
        query = self.search_input.text().lower()

        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        api_key = "pub_82776bf0a4a26c7a0a022d6600029be29e0e1"
        url = f"https://newsdata.io/api/1/news?apikey={api_key}&country=in&category=business&language=en"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    articles = data.get("results", [])
                except Exception:
                    self.scroll_layout.addWidget(QtWidgets.QLabel("Error parsing news data."))
                    return

                filtered_articles = [a for a in articles if query in a["title"].lower()] if query else articles
                categorized = {}
                others = []

                for article in filtered_articles:
                    category = self.categorize_news(article["title"])
                    if category == "OTHERS":
                        others.append(article)
                    else:
                        categorized.setdefault(category, []).append(article)

                # Add categorized articles
                for category, articles in categorized.items():
                    group_box = QtWidgets.QGroupBox(category)
                    group_box.setStyleSheet("QGroupBox { font-weight: bold; color: #8bc34a; font-size: 16px; }")
                    vbox = QtWidgets.QVBoxLayout()
                    for article in articles:
                        title = article.get("title", "Untitled")
                        link = article.get("link", "#")

                        link_frame = QtWidgets.QFrame()
                        link_frame.setStyleSheet("""
                            QFrame {
                                background-color: #1e1e1e;
                                border: 1px solid #2e2e2e;
                                border-radius: 8px;
                                padding: 8px;
                                margin-bottom: 6px;
                            }
                        """)
                        link_layout = QtWidgets.QVBoxLayout(link_frame)
                        link_layout.setContentsMargins(8, 4, 8, 4)

                        link_label = QtWidgets.QLabel(f'<a style="color: white;" href="{link}">{title}</a>')
                        link_label.setOpenExternalLinks(True)
                        link_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
                        link_label.setStyleSheet("font-size: 13px;")

                        link_layout.addWidget(link_label)
                        vbox.addWidget(link_frame)

                    group_box.setLayout(vbox)
                    self.scroll_layout.addWidget(group_box)

                # Add others section last
                if others:
                    group_box = QtWidgets.QGroupBox("OTHERS")
                    group_box.setStyleSheet("QGroupBox { font-weight: bold; color: #8bc34a; font-size: 16px; }")
                    vbox = QtWidgets.QVBoxLayout()
                    for article in others:
                        title = article.get("title", "Untitled")
                        link = article.get("link", "#")

                        link_frame = QtWidgets.QFrame()
                        link_frame.setStyleSheet("""
                            QFrame {
                                background-color: #1e1e1e;
                                border: 1px solid #2e2e2e;
                                border-radius: 8px;
                                padding: 8px;
                                margin-bottom: 6px;
                            }
                        """)
                        link_layout = QtWidgets.QVBoxLayout(link_frame)
                        link_layout.setContentsMargins(8, 4, 8, 4)

                        link_label = QtWidgets.QLabel(f'<a style="color: white;" href="{link}">{title}</a>')
                        link_label.setOpenExternalLinks(True)
                        link_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
                        link_label.setStyleSheet("font-size: 13px;")

                        link_layout.addWidget(link_label)
                        vbox.addWidget(link_frame)

                    group_box.setLayout(vbox)
                    self.scroll_layout.addWidget(group_box)

                if not filtered_articles:
                    self.scroll_layout.addWidget(QtWidgets.QLabel("No matching news found."))

            else:
                self.scroll_layout.addWidget(QtWidgets.QLabel("⚠️ Error fetching news."))

        except Exception:
            self.scroll_layout.addWidget(QtWidgets.QLabel("Network error occurred."))

    def categorize_news(self, title):
        title_lower = title.lower()
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        return "OTHERS"

    def go_home(self):
        self.close()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = NewsWindow()
    window.showMaximized()
    sys.exit(app.exec())
