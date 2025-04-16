from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class StockTableDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 2:
            text = index.data()
            if text and text.startswith("+"):
                color = QColor("#00c853")
            else:
                color = QColor("#ff5252")
                
            painter.save()
            painter.setPen(color)
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, text)
            painter.restore()
        else:
            super().paint(painter, option, index)