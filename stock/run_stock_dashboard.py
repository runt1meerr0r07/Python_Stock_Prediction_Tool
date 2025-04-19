import sys
import os
import traceback


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication
from stock.ui.dashboard import StockDashboard

# Initialize database connection
try:
    from stock.db_manager import db
    db.connect()
    print("Connected to SQLite database at", db.db_path)
    
    # Create schema if not exists
    db.create_database_schema()
    print("SQLite database schema created successfully")
    
    # Create dummy user for testing if not exists
    if not db.get_user_by_id(1):
        db.create_user("Dummy User", 100000.0)  # 1 lakh initial balance
        print("Dummy user created")
    else:
        print("Dummy user already exists")
        
except Exception as e:
    print(f"Error initializing database: {e}")
    traceback.print_exc()

def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        window = StockDashboard()
        window.show()
        
        print("Application started with SQLite database connection")
        sys.exit(app.exec())
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()