from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHBoxLayout, QInputDialog, QHeaderView
)
from PyQt6.QtCore import Qt
from stock.db_manager import db
from stock.stockapi import fetch_stock_data
from PyQt6.QtWidgets import QMenuBar, QMenu 
from PyQt6.QtGui import QAction
from stock.ui.transaction import TransactionDialog  # Import the TransactionDialog for selling stocks


class PortfolioWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Portfolio")
        self.resize(900, 600)  # Set an initial size
        self.setStyleSheet("background-color: #2a2e39; color: #e0e0e0;")

        # Enable resizing by setting the appropriate window flags
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.Window)

        # Layout
        layout = QVBoxLayout(self)
        # Add Menu Bar
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setStyleSheet("background-color: #3a3f48; color: white; font-size: 14px;")
        layout.setMenuBar(self.menu_bar)

        # Add Hamburger Menu
        self.hamburger_menu = QMenu("☰", self)
        self.hamburger_menu.setStyleSheet("background-color: #3a3f48; color: white; font-size: 14px;")
        self.menu_bar.addMenu(self.hamburger_menu)
         # Add Actions to Hamburger Menu
        self.change_username_action = QAction("Change Username", self)
        self.change_password_action = QAction("Change Password", self)
        self.logout_action = QAction("Logout", self)

        # Add actions to the menu
        self.hamburger_menu.addAction(self.change_username_action)
        self.hamburger_menu.addAction(self.change_password_action)
        self.hamburger_menu.addSeparator()
        self.hamburger_menu.addAction(self.logout_action)

        # Balance and Total Assets Section
        self.balance_label = QLabel()
        self.total_assets_label = QLabel()
        self.update_balance_and_assets()

        balance_layout = QHBoxLayout()
        balance_layout.addWidget(self.balance_label)
        balance_layout.addWidget(self.total_assets_label)
        layout.addLayout(balance_layout)

        # Portfolio Table
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(7)  # Add columns for "Add Note" and "View Note"
        self.portfolio_table.setHorizontalHeaderLabels(["Stock", "Current Price", "Change", "Quantity", "Sell", "Add Note", "View Note"])
        self.portfolio_table.horizontalHeader().setStretchLastSection(True)
        self.portfolio_table.setStyleSheet(
            "QTableWidget { background-color: #2a2e39; gridline-color: #616161; }"
            "QHeaderView::section { background-color: #3a3f48; color: #e0e0e0; }"
            "QTableWidget::item { color: #e0e0e0;font-size: 20px; }"
        )
        
        # Set all columns to have equal width
        header = self.portfolio_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.portfolio_table)

        # Notes Storage
        self.notes = {}  # Dictionary to store notes for each stock

        # Deposit Button
        deposit_button = QPushButton("Deposit Money")
        deposit_button.setStyleSheet(
            "background-color: #00b248; color: white; font-weight: bold; padding: 10px; border-radius: 5px;"
        )
        deposit_button.clicked.connect(self.deposit_money)
        layout.addWidget(deposit_button)

        # Sell All Button
        sell_all_button = QPushButton("Sell All")
        sell_all_button.setStyleSheet(
            "background-color: #d32f2f; color: white; font-weight: bold; padding: 10px; border-radius: 5px;"
        )
        sell_all_button.clicked.connect(self.sell_all_stocks)
        layout.addWidget(sell_all_button)

        # Load Portfolio Data
        self.load_portfolio()

    def update_balance_and_assets(self):
        """Update the balance and total assets labels."""
        user_id = 1  # Replace with dynamic user ID if needed
        balance = db.get_user_balance(user_id)
        holdings = db.get_user_holdings(user_id)

        # Calculate total assets
        total_assets = balance
        for holding in holdings:
            stock_ticker = holding['stock_ticker']
            quantity = holding['shares']
            current_price = self.get_current_price(stock_ticker)
            total_assets += quantity * current_price

        # Update labels
        self.balance_label.setText(f"Balance: ₹{balance:,.2f}")
        self.total_assets_label.setText(f"Total Assets: ₹{total_assets:,.2f}")

        # Style the labels
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff00;")
        self.total_assets_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff00;")

    def deposit_money(self):
        """Open a dialog to deposit money into the account."""
        user_id = 1  # Replace with dynamic user ID if needed
        try:
            # Open an input dialog to get the deposit amount
            amount, ok = QInputDialog.getDouble(self, "Deposit Money", "Enter amount to deposit:", 0, 0, 1_000_000, 2)
            if ok and amount > 0:
                # Update the user's balance in the database
                current_balance = db.get_user_balance(user_id)
                new_balance = current_balance + amount
                db.update_user_balance(user_id, new_balance)

                # Show a success message
                QMessageBox.information(self, "Success", f"₹{amount:,.2f} deposited successfully!")
                self.update_balance_and_assets()
            elif ok:
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid amount greater than 0.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to deposit money: {e}")

    def load_portfolio(self):
        """Load user's portfolio data into the table."""
        self.portfolio_table.setRowCount(0)  # Clear existing rows
        holdings = db.get_user_holdings()

        for row, holding in enumerate(holdings):
            stock_ticker = holding['stock_ticker']
            quantity = holding['shares']
            current_price = self.get_current_price(stock_ticker)
            change = self.get_price_change(stock_ticker)

            # Add data to the table
            self.portfolio_table.insertRow(row)
            self.portfolio_table.setItem(row, 0, QTableWidgetItem(stock_ticker))
            self.portfolio_table.setItem(row, 1, QTableWidgetItem(f"₹{current_price:.2f}"))

            # Color the "Change" column
            change_item = QTableWidgetItem(f"{change:+.2f}%")
            if change >= 0:
                change_item.setForeground(Qt.GlobalColor.green)
            else:
                change_item.setForeground(Qt.GlobalColor.red)
            self.portfolio_table.setItem(row, 2, change_item)

            self.portfolio_table.setItem(row, 3, QTableWidgetItem(str(quantity)))

            # Add "Sell" button
            sell_button = QPushButton("Sell")
            sell_button.setStyleSheet(
                "background-color: #d32f2f; color: white; font-weight: bold; padding: 5px 10px; border-radius: 3px;"
            )
            sell_button.clicked.connect(lambda _, s=stock_ticker, q=quantity, p=current_price: self.open_sell_dialog(s, q, p))
            self.portfolio_table.setCellWidget(row, 4, sell_button)

            # Add "Add Note" button
            add_note_button = QPushButton("Add Note")
            add_note_button.setStyleSheet(
                "background-color: #007bff; color: white; font-weight: bold; padding: 5px 10px; border-radius: 3px;"
            )
            add_note_button.clicked.connect(lambda _, s=stock_ticker: self.add_note_for_stock(s))
            self.portfolio_table.setCellWidget(row, 5, add_note_button)

            # Add "View Note" button
            view_note_button = QPushButton("View Note")
            view_note_button.setStyleSheet(
                "background-color: #6c757d; color: white; font-weight: bold; padding: 5px 10px; border-radius: 3px;"
            )
            view_note_button.clicked.connect(lambda _, s=stock_ticker: self.view_note_for_stock(s))
            self.portfolio_table.setCellWidget(row, 6, view_note_button)

        # Update balance and total assets after loading portfolio
        self.update_balance_and_assets()

    def add_note_for_stock(self, stock_ticker):
        """Add a note for a specific stock."""
        user_id = 1  # Replace with dynamic user ID if needed
        note, ok = QInputDialog.getText(self, "Add Note", f"Enter a note for {stock_ticker}:")
        if ok and note:
            # Save the note to the database
            success = db.save_stock_note(user_id, stock_ticker, note)
            if success:
                QMessageBox.information(self, "Success", f"Note added for {stock_ticker}!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to save note for {stock_ticker}.")

    def view_note_for_stock(self, stock_ticker):
        """View the note for a specific stock."""
        user_id = 1  # Replace with dynamic user ID if needed
        # Retrieve the note from the database
        note = db.get_stock_note(user_id, stock_ticker)
        if note:
            QMessageBox.information(self, f"Note for {stock_ticker}", note)
        else:
            QMessageBox.information(self, f"Note for {stock_ticker}", "No notes available for this stock.")
    def open_sell_dialog(self, stock_ticker, max_quantity, current_price):
        """Open a dialog to specify the quantity of stocks to sell."""
        success = TransactionDialog.show_dialog(self, stock_ticker, current_price, "sell")
        if success:
            # Reload portfolio to reflect changes
            self.load_portfolio()

    def sell_all_stocks(self):
        """Sell all stocks in the portfolio."""
        holdings = db.get_user_holdings()
        for holding in holdings:
            stock_ticker = holding['stock_ticker']
            quantity = holding['shares']
            current_price = self.get_current_price(stock_ticker)
            db.record_transaction(1, stock_ticker, "sell", quantity, current_price)
        QMessageBox.information(self, "Success", "All stocks sold successfully!")
        
        # Reload portfolio to reflect changes
        self.load_portfolio()

    def get_current_price(self, stock_ticker):
        """Fetch the current price of a stock."""
        try:
            stock_data = fetch_stock_data(stock_ticker)
            return stock_data.get('price', 0.0)
        except Exception as e:
            print(f"Error fetching current price for {stock_ticker}: {e}")
            return 0.0

    def get_price_change(self, stock_ticker):
        """Fetch the price change of a stock."""
        try:
            stock_data = fetch_stock_data(stock_ticker)
            current_price = stock_data.get('price', 0.0)
            historical_prices = stock_data.get('historical_prices', [])
            if historical_prices:
                previous_price = historical_prices[-2]  # Assuming the second last price is the previous close
                change = current_price - previous_price
                change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
                return change_percent
            return 0.0
        except Exception as e:
            print(f"Error fetching price change for {stock_ticker}: {e}")
            return 0.0