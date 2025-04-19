import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import webbrowser
import requests
from io import BytesIO
from yahoo_fin import news
import threading
import sys
import os
import subprocess
from stock.ui.portfolio_window import PortfolioWindow  # Import the new PortfolioWindow class


def show_page(page):
    for frame in [content_frame, news_page]:
        frame.pack_forget()
    page.pack(fill=tk.BOTH, expand=True)


def launch_test_script():
    script_path = os.path.join(os.path.dirname(__file__), 'test.py')
    print(f"Launching: {sys.executable} {script_path}")
    subprocess.Popen([sys.executable, script_path])


def launch_stock_dashboard():
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    try:
        
        loading_label = tk.Label(root, text="Loading Stock Dashboard...", font=("Arial", 18), bg='white')
        loading_label.place(relx=0.5, rely=0.5, anchor='center')
        root.update()
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stock', 'run_stock_dashboard.py')
        
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Could not find {script_path}")
        
        process = subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        root.after(1500, loading_label.destroy)
        
    except Exception as e:
        print(f"Error launching stock dashboard: {e}")
        messagebox.showerror("Error", f"Failed to launch stock dashboard: {e}")
        for widget in root.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") == "Loading Stock Dashboard...":
                widget.destroy()

def button_clicked(name):
    print(f"{name} button clicked")
    if name == "Stock":
        threading.Thread(target=launch_stock_dashboard, daemon=True).start()
    elif name == "News":
        show_page(news_page)
    elif name == "Portfolio":
        try:
            print("Opening PortfolioWindow...")
            from PyQt6.QtWidgets import QApplication
            import sys

            # Create a new QApplication instance if one doesn't already exist
            if not QApplication.instance():
                app = QApplication(sys.argv)
            else:
                app = QApplication.instance()

            portfolio_window = PortfolioWindow()  # Create the PortfolioWindow instance
            portfolio_window.exec()  # Show the window modally
            print("PortfolioWindow opened successfully.")
        except Exception as e:
            print(f"Error opening PortfolioWindow: {e}")



root = tk.Tk()
root.title("ABC Stock Advisor")
root.state('zoomed')
root.configure(bg='white')

header = tk.Frame(root, bg='gray', height=100)
header.pack(fill=tk.X)

app_name = tk.Label(header, text="ABC Stock Advisor", font=("Arial", 24, "bold"), bg='gray', fg='white')
app_name.pack(side=tk.LEFT, padx=20, pady=20)

button_frame = tk.Frame(header, bg='gray')
button_frame.pack(side=tk.RIGHT, padx=10)

icon_size = (40, 40)
icons = {
    "Stock": "stock.png",
    "Portfolio": "portfolio.png",
    "News": "news.png",
    "Notification": "notification.png",
    
}

for name, icon_path in icons.items():
    try:
        image = Image.open(icon_path).resize(icon_size)
        icon = ImageTk.PhotoImage(image)
    except:
        icon = None

    frame = tk.Frame(button_frame, bg='gray')
    frame.pack(side=tk.LEFT, padx=10)

    button = tk.Button(frame, image=icon, text=name, compound=tk.TOP, bg='gray', fg='white',
                       relief=tk.FLAT, font=("Arial", 14), command=lambda n=name: button_clicked(n))
    button.image = icon
    button.pack()

content_frame = tk.Frame(root, bg='white', padx=50, pady=50)
content_frame.pack(expand=True, fill=tk.BOTH)

title_label = tk.Label(content_frame, text="Grow Your Wealth\nThe Smart Way.", font=("Arial", 30, "bold"), bg='white', fg='black', justify=tk.LEFT)
title_label.pack(anchor='w', pady=10)

description_label = tk.Label(content_frame, text="We're revolutionizing the way investing works with data and AI-driven quantitative models.", font=("Arial", 14), bg='white', fg='gray', justify=tk.LEFT)
description_label.pack(anchor='w', pady=5)

invest_button = tk.Button(content_frame, text="Start Investing", font=("Arial", 16, "bold"), bg='black', fg='white', padx=20, pady=10)
invest_button.pack(anchor='w', pady=20)

news_page = tk.Frame(root, bg='white')

news_title = tk.Label(news_page, text="📈 Latest Stock News", font=("Arial", 24, "bold"), bg='white', fg='black', padx=20, pady=10)
news_title.pack()

news_content = tk.Frame(news_page, bg='white')
news_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

DEFAULT_IMAGE_URL = "https://www.publicdomainpictures.net/pictures/320000/velka/stock-market-chart.jpg"

def get_news_image(query):
    try:
        search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}+stock+news"
        response = requests.get(search_url)
        image_url = DEFAULT_IMAGE_URL
    except:
        image_url = DEFAULT_IMAGE_URL
    return image_url

def fetch_stock_news():
    stock_ticker = "AAPL"
    articles = news.get_yf_rss(stock_ticker)
    for widget in news_content.winfo_children():
        widget.destroy()
    if not articles:
        tk.Label(news_content, text="No news available. Check Yahoo Finance.", fg="red", bg="white").pack()
        return
    for article in articles[:10]:
        title = article["title"]
        link = article["link"]
        image_url = get_news_image(title)
        try:
            img_data = requests.get(image_url, stream=True).content
            image = Image.open(BytesIO(img_data)).resize((120, 80))
            img_tk = ImageTk.PhotoImage(image)
        except:
            img_tk = None
        news_item = tk.Frame(news_content, bg="white", pady=10, relief="solid", borderwidth=1)
        news_item.pack(fill=tk.X, padx=10, pady=5)
        if img_tk:
            img_label = tk.Label(news_item, image=img_tk, bg="white")
            img_label.image = img_tk
            img_label.pack(side=tk.LEFT, padx=10)
        news_label = tk.Label(news_item, text=title, font=("Arial", 14, "bold"), fg="blue", cursor="hand2", bg="white", wraplength=600, justify="left")
        news_label.pack(side=tk.LEFT, anchor="w", padx=10)
        news_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))

def auto_refresh_news():
    fetch_stock_news()
    root.after(60000, auto_refresh_news)

fetch_stock_news()
auto_refresh_news()

marquee_frame = tk.Frame(root, bg='black', height=30)
marquee_frame.pack(fill=tk.X, side=tk.BOTTOM)

canvas = tk.Canvas(marquee_frame, bg='black', height=30)
canvas.pack(fill=tk.BOTH, expand=True)

marquee_text = "Stock Market Updates: Stock A +1.2% | Stock B -0.5% | Stock C +2.3%  "
text_id = canvas.create_text(1500, 15, text=marquee_text, font=("Arial", 14), fill='white', anchor='w')

def scroll_text():
    canvas.move(text_id, -2, 0)
    if canvas.coords(text_id)[0] < -len(marquee_text) * 7:
        canvas.coords(text_id, 1500, 15)
    canvas.after(50, scroll_text)

scroll_text()

show_page(content_frame)
root.mainloop()