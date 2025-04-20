import tkinter as tk
from tkinter import ttk
import webbrowser
from yahoo_fin import news
import os

class NewsWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Stock News")
        self.window.configure(bg='#121212')
        self.window.geometry("1000x720")

        self.search_var = tk.StringVar()
        
        # Top Frame (for home and search bar)
        top_frame = tk.Frame(self.window, bg="#121212")
        top_frame.pack(fill="x", pady=10)

        # Home Button on the far right
        home_button = tk.Button(top_frame, text="Home", font=("Arial", 11), bg="blue", fg="white", width=10,
                                command=self.go_home)
        home_button.pack(side="right", padx=(0, 30))

        # Sub-frame for centering search entry + button
        search_frame = tk.Frame(top_frame, bg="#121212")
        search_frame.pack(anchor="center")

        # Search Bar
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 14), width=40)
        search_entry.pack(side="left", padx=(0, 5))

        # Search Button
        search_button = tk.Button(search_frame, text="Search", command=self.fetch_and_display_news,
                                  font=("Arial", 11), bg="red", fg="white", width=12)
        search_button.pack(side="left")

        

      
        # Canvas for scrollable content
        self.canvas = tk.Canvas(self.window, bg="#121212", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)

        self.scroll_frame = tk.Frame(self.canvas, bg="#121212")
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.CATEGORIES = {
            "Market Updates": ["market", "index", "indices", "nifty", "sensex", "dow", "nasdaq", "bse"],
            "Investing": ["investment", "investor", "portfolio", "mutual fund", "etf"],
            "Company News": ["earnings", "revenue", "profit", "loss", "acquisition", "merger"],
            "Regulations": ["rbi", "sebi", "regulation", "policy", "interest rate"],
            "Economy": ["gdp", "inflation", "economy", "economic", "budget", "fiscal"],
            "Crypto": ["bitcoin", "crypto", "blockchain", "ethereum"],
            "Banking": ["bank", "loan", "credit", "finance", "nbfc"]
        }

        self.fetch_and_display_news()

    def categorize_news(self, title):
        title_lower = title.lower()
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        return "Other"

    def fetch_and_display_news(self):
        query = self.search_var.get().lower()
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        try:
            articles = news.get_yf_rss("AAPL")
        except Exception as e:
            tk.Label(self.scroll_frame, text="Error fetching news", fg="red", bg="#121212").pack()
            return

        filtered_articles = [a for a in articles if query in a["title"].lower()] if query else articles

        categorized = {}
        for article in filtered_articles:
            category = self.categorize_news(article["title"])
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(article)

        ordered_categories = [cat for cat in self.CATEGORIES] + ["Other"]

        for category in ordered_categories:
            if category in categorized:
                section_frame = tk.Frame(self.scroll_frame, bg="#121212")
                section_frame.pack(anchor="center", fill="x", pady=(20, 5))

                tk.Label(section_frame, text=category, font=("Arial", 20, "bold"),
                         fg="white", bg="#121212").pack(anchor="w", padx=80, pady=(0, 10))

                for article in categorized[category]:
                    card = tk.Frame(section_frame, bg="#1e1e1e", bd=1, relief="solid", padx=10, pady=10)
                    card.pack(padx=80, pady=8, ipadx=5, ipady=5, fill="x")

                    title_label = tk.Label(card, text=article["title"], font=("Arial", 14, "bold"),
                                           fg="white", bg="#1e1e1e", wraplength=800, justify="left", cursor="hand2")
                    title_label.pack(fill="x")
                    title_label.bind("<Button-1>", lambda e, url=article["link"]: webbrowser.open(url))

    def go_home(self):
        self.window.destroy()
        os.system("python test.py")  # or provide full path if needed

def open_news_page():
    NewsWindow()
