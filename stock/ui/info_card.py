from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor

class InfoCard(QFrame):
    def __init__(self, title, value="--", parent=None, icon=None, color=None):
        super(InfoCard, self).__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setProperty("cardFrame", True)
        self.setStyleSheet("""
            background-color: #2a2e39; 
            border: 1px solid #616161; 
            border-radius: 8px;
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #aaaaaa; font-size: 13px;")
        
        header_layout.addWidget(self.title_label)
        
        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(icon).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio))
            header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        self.value_label = QLabel(value)
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        else:
            self.value_label.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold;")
        
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.value_label)
        self.setLayout(layout)
        
    def update_value(self, value, color=None):
        self.value_label.setText(str(value))
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")