import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

def button_clicked(name):
    print(f"{name} button clicked")

# Initialize main window
root = tk.Tk()
root.title("ABC Stock Advisor")
root.state('zoomed')  # Open in full screen
root.configure(bg='white')

# Header frame
header = tk.Frame(root, bg='gray', height=100)  # Increased height
header.pack(fill=tk.X)

# App name
app_name = tk.Label(header, text="ABC Stock Advisor", font=("Arial", 24, "bold"), bg='gray', fg='white')  # Increased font size
app_name.pack(side=tk.LEFT, padx=20, pady=20)

# Button frame
button_frame = tk.Frame(header, bg='gray')
button_frame.pack(side=tk.RIGHT, padx=10)

# Icons (placeholder images, replace with actual icons if needed)
icon_size = (40, 40)  # Increased icon size
icons = {
    "Stock": "stock.png",
    "Portfolio": "portfolio.png",
    "News": "news.png",
    "Notification": "notification.png",
    "Profile": "profile.png"
}

for name, icon_path in icons.items():
    try:
        image = Image.open(icon_path).resize(icon_size)
        icon = ImageTk.PhotoImage(image)
    except:
        icon = None  # If image is not found, just use text
    
    frame = tk.Frame(button_frame, bg='gray')
    frame.pack(side=tk.LEFT, padx=10)  # Increased spacing
    
    button = tk.Button(frame, image=icon, text=name, compound=tk.TOP, bg='gray', fg='white',
                       relief=tk.FLAT, font=("Arial", 14), command=lambda n=name: button_clicked(n))  # Increased font size
    button.image = icon
    button.pack()

# Main content frame (Similar to Wright UI)
content_frame = tk.Frame(root, bg='white', padx=50, pady=50)
content_frame.pack(expand=True, fill=tk.BOTH)

title_label = tk.Label(content_frame, text="Grow Your Wealth\nThe Smart Way.", font=("Arial", 30, "bold"), bg='white', fg='black', justify=tk.LEFT)
title_label.pack(anchor='w', pady=10)

description_label = tk.Label(content_frame, text="We're revolutionizing the way investing works with data and AI-driven quantitative models.", font=("Arial", 14), bg='white', fg='gray', justify=tk.LEFT)
description_label.pack(anchor='w', pady=5)

invest_button = tk.Button(content_frame, text="Start Investing", font=("Arial", 16, "bold"), bg='black', fg='white', padx=20, pady=10)
invest_button.pack(anchor='w', pady=20)

# Marquee Frame (Scrolling text at bottom, spanning entire width)
marquee_frame = tk.Frame(root, bg='black', height=30)
marquee_frame.pack(fill=tk.X, side=tk.BOTTOM)

canvas = tk.Canvas(marquee_frame, bg='black', height=30)
canvas.pack(fill=tk.BOTH, expand=True)

marquee_text = "Stock Market Updates: Stock A +1.2% | Stock B -0.5% | Stock C +2.3%  "
text_id = canvas.create_text(1500, 15, text=marquee_text, font=("Arial", 14), fill='white', anchor='w')

def scroll_text():
    canvas.move(text_id, -2, 0)  # Move text leftward
    if canvas.coords(text_id)[0] < -len(marquee_text) * 7:
        canvas.coords(text_id, 1500, 15)  # Reset position when it moves out
    canvas.after(50, scroll_text)  # Adjust speed (lower is faster)

scroll_text()

# Run the application
root.mainloop()