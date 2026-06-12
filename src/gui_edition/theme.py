from PySide6.QtWidgets import QApplication


class ThemeManager:
    _instance = None
    _dark = False
    _signal = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def is_dark(cls) -> bool:
        return cls._dark

    @classmethod
    def toggle(cls):
        cls._dark = not cls._dark
        cls._apply()
        if cls._signal:
            cls._signal(cls._dark)

    @classmethod
    def connect(cls, slot):
        cls._signal = slot

    @classmethod
    def _apply(cls):
        app = QApplication.instance()
        if not app:
            return
        app.setStyleSheet(DARK_STYLESHEET if cls._dark else LIGHT_STYLESHEET)


def _make_light():
    return f"""
* {{
    font-family: "MiSans", "Noto Sans SC", "Microsoft YaHei", "Segoe UI", sans-serif;
}}
QMainWindow, QWidget#centralWidget {{
    background: white;
}}
QFrame#sidebar {{
    background: #f7f8fa;
    border-right: 1px solid #e0e0e0;
}}
QFrame#sidebar QLabel {{
    color: #2c3e50;
    background: transparent;
}}
QFrame#sidebar QLabel#sidebarLogo {{
    color: #2c3e50;
}}
QFrame#separator {{
    background: #e0e0e0;
    border: none;
    width: 1px;
}}
QStackedWidget#contentStack {{
    background: white;
}}
QScrollArea {{
    border: none;
    background: white;
}}
QScrollArea > QWidget > QWidget {{
    background: white;
}}
QLabel {{
    color: #333;
    background: transparent;
}}
QGroupBox {{
    font-weight: bold;
    border: 1px solid #ddd;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    color: #333;
    background: transparent;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}
QLineEdit, QTextEdit, QSpinBox {{
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    background: white;
    color: #333;
    selection-background-color: #3498db;
    selection-color: white;
}}
QComboBox {{
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    background: white;
    color: #333;
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border-color: #3498db;
}}
QComboBox:focus {{
    border-color: #3498db;
}}
QComboBox::drop-down {{
    border: none;
    width: 30px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}}
QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}
QComboBox::popup {{
    border: none;
    background: white;
}}
QComboBox QAbstractItemView {{
    background: white;
    color: #333;
    border: none;
    selection-background-color: #3498db;
    selection-color: white;
    outline: none;
    padding: 2px;
}}
QProgressBar {{
    border: 1px solid #ddd;
    border-radius: 4px;
    text-align: center;
    height: 22px;
    background: #f0f0f0;
    color: #333;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2ecc71);
    border-radius: 3px;
}}
QCheckBox {{
    spacing: 8px;
    font-size: 13px;
    color: #333;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid #999;
    border-radius: 3px;
    background: white;
}}
QCheckBox::indicator:checked {{
    background: #3498db;
    border-color: #3498db;
}}
QPushButton {{
    color: #333;
}}
QPushButton#btnPrimary {{
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#btnPrimary:hover {{ background: #2980b9; }}
QPushButton#btnPrimary:disabled {{ background: #bdc3c7; color: #eee; }}
QPushButton#btnAction {{
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#btnAction:hover {{ background: #2980b9; }}
QPushButton#btnAction:disabled {{ background: #bdc3c7; color: #eee; }}
QPushButton#btnDanger {{
    background: #bdc3c7;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
}}
QPushButton#btnDanger:hover {{ background: #a9b6c2; }}
QPushButton#btnDangerActive {{
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
}}
QPushButton#btnDangerActive:hover {{ background: #c0392b; }}
QPushButton#btnSecondary {{
    background: #ecf0f1;
    color: #555;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
}}
QPushButton#btnSecondary:hover {{ background: #ddd; color: #333; }}
QTextEdit#logTerminal {{
    font-family: "MiSans", Consolas, 'Courier New', monospace;
    font-size: 12px;
    background: #f5f5f5;
    color: #333;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 10px;
}}
QLabel#hintBox {{
    color: #666;
    font-size: 12px;
    padding: 10px;
    background: #f0f0f0;
    border-radius: 6px;
}}
QFrame#saveFrame {{
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 8px;
}}
QLabel#statusOk {{
    color: #27ae60;
    font-size: 12px;
    background: transparent;
}}
QLabel#statusError {{
    color: #e74c3c;
    font-size: 12px;
    background: transparent;
}}
QScrollBar:vertical {{
    width: 8px;
    background: transparent;
}}
QScrollBar::handle:vertical {{
    background: #ccc;
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: #aaa; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QMessageBox {{ background: white; color: #333; }}
QFileDialog {{ background: white; color: #333; }}
"""


def _make_dark():
    return f"""
* {{
    font-family: "MiSans", "Noto Sans SC", "Microsoft YaHei", "Segoe UI", sans-serif;
}}
QMainWindow, QWidget#centralWidget {{
    background: #1e1e1e;
}}
QFrame#sidebar {{
    background: #252526;
    border-right: 1px solid #3c3c3c;
}}
QFrame#sidebar QLabel {{
    color: #d4d4d4;
    background: transparent;
}}
QFrame#sidebar QLabel#sidebarLogo {{
    color: #e0e0e0;
}}
QFrame#separator {{
    background: #3c3c3c;
    border: none;
    width: 1px;
}}
QStackedWidget#contentStack {{
    background: #1e1e1e;
}}
QScrollArea {{
    border: none;
    background: #1e1e1e;
}}
QScrollArea > QWidget > QWidget {{
    background: #1e1e1e;
}}
QLabel {{
    color: #d4d4d4;
    background: transparent;
}}
QGroupBox {{
    font-weight: bold;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    color: #d4d4d4;
    background: transparent;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}
QLineEdit, QTextEdit, QSpinBox {{
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    background: #2d2d2d;
    color: #d4d4d4;
    selection-background-color: #264f78;
}}
QComboBox {{
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    background: #2d2d2d;
    color: #d4d4d4;
    selection-background-color: #264f78;
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border-color: #3498db;
}}
QComboBox:focus {{
    border-color: #3498db;
}}
QComboBox::drop-down {{
    border: none;
    width: 30px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}}
QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}
QComboBox::popup {{
    border: none;
    background: #2d2d2d;
}}
QComboBox QAbstractItemView {{
    background: #2d2d2d;
    color: #d4d4d4;
    border: none;
    selection-background-color: #3498db;
    selection-color: #ffffff;
    outline: none;
    padding: 2px;
}}
QProgressBar {{
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    text-align: center;
    height: 22px;
    background: #2d2d2d;
    color: #d4d4d4;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2ecc71);
    border-radius: 3px;
}}
QCheckBox {{
    spacing: 8px;
    font-size: 13px;
    color: #d4d4d4;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid #888;
    border-radius: 3px;
    background: #2d2d2d;
}}
QCheckBox::indicator:checked {{
    background: #3498db;
    border-color: #3498db;
}}
QPushButton {{
    color: #d4d4d4;
}}
QPushButton#btnPrimary {{
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#btnPrimary:hover {{ background: #2980b9; }}
QPushButton#btnPrimary:disabled {{ background: #555; color: #999; }}
QPushButton#btnAction {{
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#btnAction:hover {{ background: #2980b9; }}
QPushButton#btnAction:disabled {{ background: #555; color: #999; }}
QPushButton#btnDanger {{
    background: #555;
    color: #999;
    border: none;
    border-radius: 6px;
    font-size: 14px;
}}
QPushButton#btnDanger:hover {{ background: #666; }}
QPushButton#btnDangerActive {{
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
}}
QPushButton#btnDangerActive:hover {{ background: #c0392b; }}
QPushButton#btnSecondary {{
    background: #333;
    color: #ccc;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
}}
QPushButton#btnSecondary:hover {{ background: #444; color: #fff; }}
QTextEdit#logTerminal {{
    font-family: "MiSans", Consolas, 'Courier New', monospace;
    font-size: 12px;
    background: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 10px;
}}
QLabel#hintBox {{
    color: #aaa;
    font-size: 12px;
    padding: 10px;
    background: #2d2d2d;
    border-radius: 6px;
}}
QFrame#saveFrame {{
    background: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
}}
QLabel#statusOk {{
    color: #27ae60;
    font-size: 12px;
    background: transparent;
}}
QLabel#statusError {{
    color: #e74c3c;
    font-size: 12px;
    background: transparent;
}}
QScrollBar:vertical {{
    width: 8px;
    background: transparent;
}}
QScrollBar::handle:vertical {{
    background: #424242;
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: #555; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QMessageBox {{ background: #1e1e1e; color: #d4d4d4; }}
QFileDialog {{ background: #1e1e1e; color: #d4d4d4; }}
"""


LIGHT_STYLESHEET = _make_light()
DARK_STYLESHEET = _make_dark()


def init_theme():
    ThemeManager.instance()
