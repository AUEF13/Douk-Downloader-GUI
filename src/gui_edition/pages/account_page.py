from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QGroupBox,
    QProgressBar, QComboBox, QSpinBox, QCheckBox,
    QFormLayout, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, Slot, QThread

from ..theme import ThemeManager


class AccountWorker(QThread):
    progress = Signal(str, str)
    finished = Signal(bool, str)

    def __init__(self, bridge, async_thread, urls, mode, tiktok=False, max_pages=0):
        super().__init__()
        self.bridge = bridge
        self.async_thread = async_thread
        self.urls = urls
        self.mode = mode
        self.tiktok = tiktok
        self.max_pages = max_pages
        self._cancelled = False

    def run(self):
        try:
            future = self.async_thread.run_coro(
                self.bridge.download_account(self.urls, self.mode, self.tiktok, self.max_pages)
            )
            if future:
                result = future.result(timeout=3600)
                if self._cancelled:
                    self.finished.emit(False, "已取消")
                    return
                s = result.get("success", 0)
                f = result.get("failed", 0)
                self.finished.emit(True, f"采集完成: 成功 {s} 个, 失败 {f} 个")
            else:
                self.finished.emit(False, "无法启动采集任务")
        except Exception as e:
            self.finished.emit(False, f"采集出错: {e}")

    def cancel(self):
        self._cancelled = True


class AccountPage(QWidget):
    log_message = Signal(str)

    def __init__(self, bridge=None, async_thread=None, parent=None):
        super().__init__(parent)
        self.bridge = bridge
        self.async_thread = async_thread
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        self.outer = QVBoxLayout(self)
        self.outer.setContentsMargins(0, 0, 0, 0)
        self.outer.setSpacing(0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.outer.addWidget(self.scroll)
        self.container = QWidget()
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.header = QLabel("账号下载")
        hf = self.header.font()
        hf.setPointSize(18)
        hf.setBold(True)
        self.header.setFont(hf)
        layout.addWidget(self.header)

        url_group = QGroupBox("账号链接")
        ul = QVBoxLayout(url_group)
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("输入账号主页链接，每行一个\n抖音: https://www.douyin.com/user/xxx\nTikTok: https://www.tiktok.com/@xxx")
        self.url_input.setMaximumHeight(120)
        ul.addWidget(self.url_input)
        layout.addWidget(url_group)

        opt_group = QGroupBox("下载选项")
        ol = QVBoxLayout(opt_group)
        ol.setSpacing(12)
        ol.setContentsMargins(16, 20, 16, 16)
        r1 = QHBoxLayout()
        r1.setSpacing(20)
        r1.addWidget(QLabel("下载类型:"))
        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumHeight(36)
        self.mode_combo.setMinimumWidth(160)
        self.mode_combo.addItems(["发布作品", "喜欢作品", "收藏作品"])
        r1.addWidget(self.mode_combo)
        self.tiktok_check = QCheckBox("TikTok 平台")
        r1.addWidget(self.tiktok_check)
        r1.addStretch()
        ol.addLayout(r1)
        r2 = QHBoxLayout()
        r2.setSpacing(20)
        r2.addWidget(QLabel("最大页数:"))
        self.max_pages = QSpinBox()
        self.max_pages.setRange(0, 99999)
        self.max_pages.setValue(0)
        self.max_pages.setSpecialValueText("不限制")
        self.max_pages.setMinimumHeight(36)
        self.max_pages.setMinimumWidth(120)
        r2.addWidget(self.max_pages)
        r2.addStretch()
        ol.addLayout(r2)
        layout.addWidget(opt_group)

        bl = QHBoxLayout()
        self.start_btn = QPushButton("开始采集")
        self.start_btn.setMinimumHeight(44)
        self.start_btn.setMinimumWidth(140)
        self.start_btn.setObjectName("btnAction")
        self.start_btn.clicked.connect(self._on_start)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setMinimumHeight(44)
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.setObjectName("btnDanger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        bl.addWidget(self.start_btn)
        bl.addWidget(self.stop_btn)
        bl.addStretch()
        layout.addLayout(bl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(24)
        layout.addWidget(self.progress_bar)

        log_group = QGroupBox("采集日志")
        ll = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setObjectName("logTerminal")
        ll.addWidget(self.log_text)
        layout.addWidget(log_group)

        layout.addStretch()
        self.scroll.setWidget(self.container)

    def update_theme(self, dark):
        pass

    @Slot()
    def _on_start(self):
        urls = self.url_input.toPlainText().strip().split("\n")
        urls = [u.strip() for u in urls if u.strip()]
        if not urls:
            self.log_text.append("[警告] 请输入至少一个账号链接")
            return
        mode_map = {"发布作品": "post", "喜欢作品": "favorite", "收藏作品": "collection"}
        mode = mode_map.get(self.mode_combo.currentText(), "post")
        tiktok = self.tiktok_check.isChecked()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_text.clear()
        self.log_text.append(f"[信息] 开始采集 {len(urls)} 个账号...")
        self._worker = AccountWorker(self.bridge, self.async_thread, urls, mode, tiktok, self.max_pages.value())
        self._worker.progress.connect(lambda msg, lv: self.log_text.append(f"[{lv}] {msg}"))
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_stop(self):
        if self._worker:
            self._worker.cancel()
            self.log_text.append("[信息] 正在取消...")

    def _on_finished(self, success, msg):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_text.append(f"[{'完成' if success else '错误'}] {msg}")
        self.progress_bar.setVisible(False)
        self._worker = None
        self.log_message.emit(msg)
