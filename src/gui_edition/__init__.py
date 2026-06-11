import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .main_window import MainWindow
from .theme import ThemeManager, init_theme, LIGHT_STYLESHEET

__all__ = ["run_gui"]


def run_gui():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    init_theme()
    ThemeManager.connect(lambda dark: _on_theme_changed(app, dark))

    app.setStyleSheet(LIGHT_STYLESHEET)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def _on_theme_changed(app: QApplication, dark: bool):
    from .theme import ThemeManager
    ThemeManager._apply()
