import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import Qt

from .main_window import MainWindow
from .theme import ThemeManager, init_theme, LIGHT_STYLESHEET

__all__ = ["run_gui"]


def _load_fonts():
    font_dir = Path(__file__).parent.parent.parent / "fonts"
    if not font_dir.exists():
        return
    for f in font_dir.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(f))


def run_gui():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    _load_fonts()

    init_theme()
    ThemeManager.connect(lambda dark: _on_theme_changed(app, dark))

    app.setStyleSheet(LIGHT_STYLESHEET)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def _on_theme_changed(app: QApplication, dark: bool):
    from .theme import ThemeManager
    ThemeManager._apply()
