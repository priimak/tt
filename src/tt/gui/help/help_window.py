from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget, QLabel
from pytide6 import VBoxLayout

from tt.gui.help import HELP


class HelpWindow(QWidget):
    def __init__(self, parent, help_name: str):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        pallete = QPalette()
        pallete.setColor(QPalette.ColorRole.Window, QColor(0xfe, 0xfc, 0xaf))
        self.setPalette(pallete)
        self.text = QLabel(HELP[help_name])
        self.setLayout(VBoxLayout([self.text]))

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.close()
