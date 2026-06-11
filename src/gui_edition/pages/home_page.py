from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..theme import ThemeManager


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("DucK")
        self.title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(72)
        title_font.setBold(True)
        self.title.setFont(title_font)
        layout.addWidget(self.title)

    def update_theme(self, dark: bool):
        self._dark = dark
        if dark:
            self.title.setStyleSheet("color: #d4d4d4;")
        else:
            self.title.setStyleSheet("color: #2c3e50;")
