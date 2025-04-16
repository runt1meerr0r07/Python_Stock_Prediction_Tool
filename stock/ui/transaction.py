from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QGridLayout, QSpinBox, QFrame)
from PyQt6.QtCore import Qt, QTimer, QEventLoop
from PyQt6.QtGui import QPixmap
import os

class TransactionDialog(QWidget):
    def __init__(self, parent=None, stock_symbol="", stock_price=0, action="buy"):
        super().__init__(parent, Qt.WindowType.Window)
        
        self.stock_symbol = stock_symbol
        self.stock_price = stock_price
        self.action = action
        self.quantity = 1
        self.result = False
        
        from stock.db_manager import db
        self.user_balance = db.get_user_balance()
        
        self.parent_stock_page = parent
        
        if action == "buy":
            self.setWindowTitle(f"Buy {stock_symbol}")
        else:
            self.setWindowTitle(f"Sell {stock_symbol}")
            
        self.setFixedSize(400, 500)
        self.setStyleSheet("background-color: #2a2e39; color: #e0e0e0;")
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        if self.action == "buy":
            icon_label = QLabel()
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "buy_icon.png")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("🛒")
                icon_label.setStyleSheet("font-size: 48px; color: #00c853;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(icon_label)
        else:
            icon_label = QLabel()
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "sell_icon.png")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("💸")
                icon_label.setStyleSheet("font-size: 48px; color: #ff5252;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(icon_label)
            
        title_label = QLabel(f"{'Buy' if self.action == 'buy' else 'Sell'} {self.stock_symbol}")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        price_label = QLabel("Current Price:")
        price_label.setStyleSheet("color: #e0e0e0;")
        
        price_value = QLabel(f"₹{self.stock_price:.2f}")
        price_value.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        form_layout.addWidget(price_label, 0, 0)
        form_layout.addWidget(price_value, 0, 1)
        
        qty_label = QLabel("Quantity:")
        qty_label.setStyleSheet("color: #e0e0e0;")
        
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(10000)
        self.qty_spin.setValue(1)
        self.qty_spin.setStyleSheet("font-size: 18px;")
        self.qty_spin.valueChanged.connect(self.update_total)
        
        form_layout.addWidget(qty_label, 1, 0)
        form_layout.addWidget(self.qty_spin, 1, 1)
        
        total_label = QLabel("Total Cost:")
        total_label.setStyleSheet("color: #e0e0e0;")
        
        self.total_value = QLabel(f"₹{self.stock_price:.2f}")
        self.total_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #00c853;")
        
        form_layout.addWidget(total_label, 2, 0)
        form_layout.addWidget(self.total_value, 2, 1)
        
        balance_label = QLabel("Available Balance:")
        balance_label.setStyleSheet("color: #e0e0e0;")
        
        self.balance_value = QLabel(f"₹{self.user_balance:.2f}")
        self.balance_value.setStyleSheet("font-size: 16px; color: #e0e0e0;")
        
        form_layout.addWidget(balance_label, 3, 0)
        form_layout.addWidget(self.balance_value, 3, 1)
        
        main_layout.addLayout(form_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        info_text = ""
        if self.action == "buy":
            max_qty = int(self.user_balance / self.stock_price)
            info_text = f"You can buy up to {max_qty} shares with your current balance."
        else:
            info_text = "Selling shares will credit your account immediately."
            
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #e0e0e0;")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        
        confirm_text = "Buy Now" if self.action == "buy" else "Sell Now"
        self.confirm_button = QPushButton(confirm_text)
        self.confirm_button.clicked.connect(self.accept)
        if self.action == "buy":
            self.confirm_button.setStyleSheet("background-color: #00c853;")
        else:
            self.confirm_button.setStyleSheet("background-color: #ff5252;")
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.confirm_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def update_total(self):
        self.quantity = self.qty_spin.value()
        total = self.quantity * self.stock_price
        self.total_value.setText(f"₹{total:.2f}")
        
        if self.action == "buy" and total > self.user_balance:
            self.total_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #ff5252;")
            self.confirm_button.setEnabled(False)
        else:
            color = "#00c853" if self.action == "buy" else "#ff5252"
            self.total_value.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
            self.confirm_button.setEnabled(True)
        
    def accept(self):
        from stock.db_manager import db
        
        try:
            if self.action == "buy":
                
                total_cost = self.quantity * self.stock_price
                if total_cost > self.user_balance:
                    print(f"Error: Insufficient balance to buy {self.quantity} shares of {self.stock_symbol}")
                    self.result = False
                    self.close()
                    return
                    
                # Record the transaction
                db.record_transaction(1, self.stock_symbol, "buy", self.quantity, self.stock_price)
                
                # Update user balance
                db.update_user_balance(1, self.user_balance - total_cost)
                
                print(f"Successfully bought {self.quantity} shares of {self.stock_symbol} for ₹{total_cost:.2f}")
            else:
                # Check if user has enough shares to sell
                holdings = db.get_user_holdings()
                user_shares = 0
                
                for holding in holdings:
                    if holding['stock_ticker'] == self.stock_symbol:
                        user_shares = holding['shares']
                        break
                        
                if user_shares < self.quantity:
                    print(f"Error: You only have {user_shares} shares of {self.stock_symbol} to sell")
                    self.result = False
                    self.close()
                    return
                    
                # Record the transaction
                total_amount = self.quantity * self.stock_price
                db.record_transaction(1, self.stock_symbol, "sell", self.quantity, self.stock_price)
                
                # Update user balance
                db.update_user_balance(1, self.user_balance + total_amount)
                
                print(f"Successfully sold {self.quantity} shares of {self.stock_symbol} for ₹{total_amount:.2f}")
            
            self.result = True
            
            # Force an update of the holdings display
            if self.parent_stock_page:
                QTimer.singleShot(100, self.parent_stock_page.update_holdings_info)
                QTimer.singleShot(100, self.parent_stock_page.update_user_balance_display)
                
            self.close()
        except Exception as e:
            print(f"Transaction error: {e}")
            self.result = False
            self.close()
        
    def reject(self):
        self.result = False
        self.close()
        
    @staticmethod
    def show_dialog(parent, stock_symbol, stock_price, action="buy"):
        dialog = TransactionDialog(parent, stock_symbol, stock_price, action)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.show()
        
        loop = QEventLoop()
        dialog.destroyed.connect(loop.quit)
        loop.exec()
        
        return dialog.result