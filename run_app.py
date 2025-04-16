import sys
import os

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock'))
except:
    pass

try:
    from PyQt6.QtWidgets import QApplication
    print("PyQt6 imported successfully")
except ImportError as e:
    print(f"ERROR importing PyQt6: {e}")
    sys.exit(1)

try:
    import matplotlib
    import numpy as np
    import pandas as pd
    import yfinance as yf
    print("Dependencies imported successfully")
except ImportError as e:
    print(f"ERROR importing dependencies: {e}")
    sys.exit(1)

try:
    from stock.db_manager import DatabaseManager
    print("Database manager imported successfully")
except ImportError as e:
    print(f"ERROR importing database manager: {e}")

try:
    print("Attempting to import and run the application...")
    from stock.stock_page import StockDashboard, QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    print("Creating window...")
    window = StockDashboard()
    print("Showing window...")
    window.show()
    print("Starting application loop...")
    sys.exit(app.exec())
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nApplication failed to start. Press Enter to exit...")
    input()