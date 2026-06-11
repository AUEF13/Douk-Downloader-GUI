import asyncio
import sys
from pathlib import Path
from asyncio import new_event_loop
from threading import Event, Thread

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QApplication, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QFont, QPixmap

from .bridge import GUIBridge
from .theme import ThemeManager, init_theme
from .pages import (
    HomePage, DownloadPage, AccountPage,
    CookiePage, SettingsPage, LogPage,
)


class SidebarButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setMinimumHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        dark = ThemeManager.is_dark()
        if dark:
            self.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    color: #bbb;
                    background: transparent;
                }
                QPushButton:hover {
                    background: #2a2d2e;
                    color: #e0e0e0;
                }
                QPushButton:checked {
                    background: #094771;
                    color: #ffffff;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    color: #555;
                    background: transparent;
                }
                QPushButton:hover {
                    background: #ecf0f1;
                    color: #2c3e50;
                }
                QPushButton:checked {
                    background: #3498db;
                    color: white;
                    font-weight: bold;
                }
            """)

    def refresh_style(self):
        self._update_style()


class AsyncThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop: asyncio.AbstractEventLoop | None = None
        self._ready = Event()

    def run(self):
        self.loop = new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._ready.set()
        self.loop.run_forever()

    def wait_ready(self):
        self._ready.wait()

    def run_coro(self, coro):
        if self.loop and self.loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, self.loop)
        return None

    def stop(self):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DucK-Downloader-GUI v1.0.2")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 750)

        init_theme()

        self._async_thread = AsyncThread()
        self._async_thread.start()
        self._async_thread.wait_ready()

        self.bridge = GUIBridge(log_callback=self._on_log)
        self._init_bridge()

        self._setup_ui()
        self._connect_signals()

        self._apply_theme_button()
        self.sidebar_buttons[0].setChecked(True)
        self._update_sidebar_for_page()

    def _init_bridge(self):
        future = self._async_thread.run_coro(self.bridge.initialize())
        if future:
            try:
                future.result(timeout=30)
            except Exception as e:
                print(f"Bridge init error: {e}")

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 24, 12, 16)
        sidebar_layout.setSpacing(4)

        logo_path = str(Path(__file__).parent / "assets" / "logo.png")
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap(logo_path).scaled(160, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setObjectName("sidebarLogo")
        sidebar_layout.addWidget(self.logo_label)

        sidebar_layout.addSpacing(8)

        nav_items = [
            "首页",
            "作品下载",
            "账号下载",
            "Cookie 管理",
            "设置",
            "日志",
        ]

        self.sidebar_buttons: list[SidebarButton] = []
        for text in nav_items:
            btn = SidebarButton(text)
            btn.clicked.connect(lambda checked, b=btn: self._on_nav_click(b))
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        sidebar_layout.addStretch()

        self.theme_btn = QPushButton()
        self.theme_btn.setMinimumHeight(38)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        sidebar_layout.addWidget(self.theme_btn)

        sidebar_layout.addSpacing(4)

        self.version_label = QLabel("v1.0.2")
        self.version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.version_label)

        main_layout.addWidget(self.sidebar)

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setObjectName("separator")
        main_layout.addWidget(self.separator)

        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")

        self.home_page = HomePage()
        self.download_page = DownloadPage(bridge=self.bridge, async_thread=self._async_thread)
        self.account_page = AccountPage(bridge=self.bridge, async_thread=self._async_thread)
        self.cookie_page = CookiePage(bridge=self.bridge, async_thread=self._async_thread)
        self.settings_page = SettingsPage(bridge=self.bridge, async_thread=self._async_thread)
        self.log_page = LogPage()

        self.content_stack.addWidget(self.home_page)
        self.content_stack.addWidget(self.download_page)
        self.content_stack.addWidget(self.account_page)
        self.content_stack.addWidget(self.cookie_page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.addWidget(self.log_page)

        main_layout.addWidget(self.content_stack)

    def _connect_signals(self):
        self.download_page.log_message.connect(
            lambda msg: self.log_page.append_log(msg, "info")
        )
        self.account_page.log_message.connect(
            lambda msg: self.log_page.append_log(msg, "info")
        )

    def _on_theme_changed(self, dark: bool):
        self._apply_sidebar_theme(dark)
        self._apply_theme_button()

        current = self.content_stack.currentIndex()
        for btn in self.sidebar_buttons:
            btn.refresh_style()

        if 0 <= current < len(self.sidebar_buttons):
            self.sidebar_buttons[current].setChecked(True)
        self._update_sidebar_for_page()

    def _toggle_theme(self):
        ThemeManager.toggle()
        self._on_theme_changed(ThemeManager.is_dark())

    def _apply_theme_button(self):
        dark = ThemeManager.is_dark()
        if dark:
            self.theme_btn.setText("亮色模式")
            self.theme_btn.setStyleSheet("""
                QPushButton {
                    background: #333;
                    color: #ccc;
                    border: 1px solid #555;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 12px;
                }
                QPushButton:hover { background: #3a3a3a; color: #fff; }
            """)
        else:
            self.theme_btn.setText("深色模式")
            self.theme_btn.setStyleSheet("""
                QPushButton {
                    background: #ecf0f1;
                    color: #666;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 12px;
                }
                QPushButton:hover { background: #ddd; color: #333; }
            """)

    def _apply_sidebar_theme(self, dark: bool):
        if dark:
            self.sidebar.setStyleSheet("""
                QFrame#sidebar {
                    background-color: #252526;
                    border-right: 1px solid #3c3c3c;
                }
                QLabel#sidebarLogo {
                    color: #e0e0e0;
                    background: transparent;
                }
                QLabel {
                    color: #888;
                    background: transparent;
                }
            """)
            self.separator.setStyleSheet("background: #3c3c3c; border: none; width: 1px;")
            self.version_label.setStyleSheet("color: #555; font-size: 11px; background: transparent;")
        else:
            self.sidebar.setStyleSheet("""
                QFrame#sidebar {
                    background-color: #f7f8fa;
                    border-right: 1px solid #e0e0e0;
                }
                QLabel#sidebarLogo {
                    color: #2c3e50;
                    background: transparent;
                }
                QLabel {
                    color: #888;
                    background: transparent;
                }
            """)
            self.separator.setStyleSheet("background: #e0e0e0; border: none; width: 1px;")
            self.version_label.setStyleSheet("color: #aaa; font-size: 11px; background: transparent;")

    def _on_nav_click(self, clicked_btn: SidebarButton):
        for i, btn in enumerate(self.sidebar_buttons):
            if btn == clicked_btn:
                btn.setChecked(True)
                self.content_stack.setCurrentIndex(i)
            else:
                btn.setChecked(False)
        self._update_sidebar_for_page()

    def _update_sidebar_for_page(self):
        is_home = self.content_stack.currentIndex() == 0
        dark = ThemeManager.is_dark()
        if is_home:
            self.sidebar.setStyleSheet("QFrame#sidebar { background: transparent; border-right: none; }")
            self.separator.setStyleSheet("background: transparent; border: none; width: 1px;")
            if dark:
                self.home_page.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1f2e, stop:1 #1a2332);")
            else:
                self.home_page.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e8f4fd, stop:1 #f0f4ff);")
        else:
            self._apply_sidebar_theme(dark)
            self.home_page.setStyleSheet("")

    def _switch_page(self, index: int):
        if 0 <= index < len(self.sidebar_buttons):
            for i, btn in enumerate(self.sidebar_buttons):
                btn.setChecked(i == index)
            self.content_stack.setCurrentIndex(index)

    @Slot(str, str)
    def _on_log(self, message: str, level: str = "info"):
        QTimer.singleShot(0, lambda: self.log_page.append_log(message, level))

    def closeEvent(self, event):
        future = self._async_thread.run_coro(self.bridge.close())
        if future:
            try:
                future.result(timeout=5)
            except Exception:
                pass
        self._async_thread.stop()
        event.accept()
