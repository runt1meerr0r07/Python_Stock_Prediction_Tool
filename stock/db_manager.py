import os
import sqlite3
from dotenv import load_dotenv

try:
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not found, using default values")


class DatabaseManager:
    def __init__(self, fallback_mode=False):
        self.connection = None
        self.fallback_mode = fallback_mode
        self.simulated_holdings = {}
        self.db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'portfolio.db')
        self.db_path = self.db_file

    def connect(self):
        if self.fallback_mode:
            print("Using fallback mode without database connection")
            return True

        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row
            print(f"Connected to SQLite database at {self.db_file}")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.fallback_mode = True
            return False

    def create_database_schema(self):
        if self.fallback_mode:
            return True

        cursor = self.connection.cursor()
        try:
            # Create user table
            cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                total_assets REAL DEFAULT 0,
                profit_loss REAL DEFAULT 0
            )''')

            # Create stock_transactions table
            cursor.execute('''CREATE TABLE IF NOT EXISTS stock_transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stock_ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                transaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(user_id)
            )''')

            # Create watchlist table
            cursor.execute('''CREATE TABLE IF NOT EXISTS watchlist (
                watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stock_ticker TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(user_id),
                UNIQUE(user_id, stock_ticker)
            )''')

            self.connection.commit()
            print("SQLite database schema created successfully")
            return True
        except Exception as e:
            print(f"Error creating SQLite database schema: {e}")
            return False

    def close(self):
        if not self.fallback_mode and self.connection:
            self.connection.close()
            print("Database connection closed")

    def execute_query(self, query, params=None, fetch=False):
        if self.fallback_mode:
            return self._simulate_query_result(query, params, fetch)

        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()

            if fetch:
                return [dict(row) for row in cursor.fetchall()]
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None

    def _simulate_query_result(self, query, params=None, fetch=False):
        if not fetch:
            return None

        if "SELECT * FROM user WHERE username" in query:
            return [{'user_id': 1, 'username': 'demo_user', 'password': 'password123',
                     'total_assets': 100000.00, 'profit_loss': 0.00}]
        elif "SELECT total_assets FROM user" in query:
            return [{'total_assets': 100000.00}]
        elif "SELECT * FROM stock_transactions" in query:
            return []
        elif "SELECT stock_ticker, SUM" in query:
            return [{'stock_ticker': ticker, 'shares': shares}
                    for ticker, shares in self.simulated_holdings.items()]
        elif "SELECT stock_ticker FROM watchlist" in query:
            return []
        else:
            return []

    def get_user_balance(self, user_id=1):
        if self.fallback_mode:
            return 100000.00  # Default balance in fallback mode

        query = "SELECT total_assets FROM user WHERE user_id = ?"
        result = self.execute_query(query, (user_id,), fetch=True)

        if result and len(result) > 0:
            return result[0]['total_assets']
        return 0.0

    def update_user_balance(self, user_id, new_balance):
        if self.fallback_mode:
            print(f"Simulated balance update: {new_balance}")
            return True

        query = "UPDATE user SET total_assets = ? WHERE user_id = ?"
        return self.execute_query(query, (new_balance, user_id))

    def record_transaction(self, user_id, stock_ticker, action, quantity, price):
        if self.fallback_mode:
            if action == 'buy':
                if stock_ticker in self.simulated_holdings:
                    self.simulated_holdings[stock_ticker] += quantity
                else:
                    self.simulated_holdings[stock_ticker] = quantity
            else:
                if stock_ticker in self.simulated_holdings:
                    self.simulated_holdings[stock_ticker] -= quantity
                    if self.simulated_holdings[stock_ticker] <= 0:
                        del self.simulated_holdings[stock_ticker]

            print(f"Simulated transaction: {action} {quantity} shares of {stock_ticker} at ₹{price}")
            return True

        query = "INSERT INTO stock_transactions (user_id, stock_ticker, action, quantity, price, transaction_date) VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))"
        params = (user_id, stock_ticker, action, quantity, price)
        return self.execute_query(query, params)

    def get_user_transactions(self, user_id=1):
        query = "SELECT * FROM stock_transactions WHERE user_id = ? ORDER BY transaction_date DESC"
        return self.execute_query(query, (user_id,), fetch=True)

    def get_user_holdings(self, user_id=1):
        if self.fallback_mode:
            return [{'stock_ticker': ticker, 'shares': shares}
                    for ticker, shares in self.simulated_holdings.items()]

        query = """
        SELECT stock_ticker, 
               SUM(CASE WHEN action = 'buy' THEN quantity ELSE -quantity END) as shares,
               SUM(CASE WHEN action = 'buy' THEN quantity * price ELSE -quantity * price END) as cost_basis
        FROM stock_transactions 
        WHERE user_id = ? 
        GROUP BY stock_ticker 
        HAVING shares > 0
        """
        return self.execute_query(query, (user_id,), fetch=True)

    def get_user_by_id(self, user_id):
        if self.fallback_mode:
            return {'user_id': 1, 'username': 'demo_user', 'total_assets': 100000.00}

        query = "SELECT * FROM user WHERE user_id = ?"
        result = self.execute_query(query, (user_id,), fetch=True)

        if result and len(result) > 0:
            return result[0]
        return None

    def validate_user(self, username, password):
        """Validate user credentials."""
        query = "SELECT * FROM user WHERE username = ? AND password = ?"
        result = self.execute_query(query, (username, password), fetch=True)
        return bool(result)

    def register_user(self, username, password):
        """Register a new user."""
        try:
            query = "INSERT INTO user (username, password, total_assets) VALUES (?, ?, ?)"
            self.execute_query(query, (username, password, 100000.0))  # Default balance: 1 lakh
            return True
        except Exception as e:
            print(f"Error registering user: {e}")
            return False


# Initialize database manager
db = DatabaseManager()

try:
    db.connect()
    db.create_database_schema()
    print("Database initialized successfully.")
except Exception as e:
    print(f"Error initializing database: {e}")