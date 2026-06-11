from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QLineEdit, QGroupBox,
    QProgressBar, QCheckBox, QSpinBox, QComboBox,
    QFormLayout, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, Slot, QThread

from ..theme import ThemeManager


class DownloadWorker(QThread):
    progress = Signal(str, str)
    finished = Signal(bool, str)

    def __init__(self, bridge, async_thread, urls, tiktok=False):
        super().__init__()
        self.bridge = bridge
        self.async_thread = async_thread
        self.urls = urls
        self.tiktok = tiktok
        self._cancelled = False

    def run(self):
        try:
            future = self.async_thread.run_coro(self.bridge.download_detail(self.urls, self.tiktok))
            if future:
                result = future.result(timeout=600)
                if self._cancelled:
                    self.finished.emit(False, "已取消")
                    return
                s = result.get("success", 0)
                f = result.get("failed", 0)
                self.finished.emit(True, f"下载完成: 成功 {s} 个, 失败 {f} 个")
            else:
                self.finished.emit(False, "无法启动下载任务")
        except Exception as e:
            self.finished.emit(False, f"下载出错: {e}")

    def cancel(self):
        self._cancelled = True


class DownloadPage(QWidget):
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

        self.header = QLabel("作品下载")
        hf = self.header.font()
        hf.setPointSize(18)
        hf.setBold(True)
        self.header.setFont(hf)
        layout.addWidget(self.header)

        input_group = QGroupBox("链接输入")
        il = QVBoxLayout(input_group)
        il.setContentsMargins(16, 20, 16, 16)
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText(
            "输入抖音/TikTok 作品链接，每行一个\n"
            "支持格式:\n"
            "  抖音: https://www.douyin.com/video/xxx\n"
            "  TikTok: https://www.tiktok.com/@user/video/xxx"
        )
        self.url_input.setMaximumHeight(100)
        il.addWidget(self.url_input)
        layout.addWidget(input_group)

        opts_group = QGroupBox("下载选项")
        ol = QHBoxLayout(opts_group)
        ol.setContentsMargins(16, 20, 16, 16)
        ol.setSpacing(24)
        fl = QFormLayout()
        fl.setSpacing(8)
        fl.addRow(QCheckBox("TikTok 平台"))
        fl.addRow(QCheckBox("下载音乐"))
        fl.addRow(QCheckBox("下载封面"))
        fl.addRow(QCheckBox("按作品分文件夹"))
        ol.addLayout(fl)
        fl2 = QFormLayout()
        fl2.setSpacing(8)
        self.max_retry = QSpinBox()
        self.max_retry.setRange(0, 10)
        self.max_retry.setValue(5)
        self.max_retry.setMinimumHeight(32)
        fl2.addRow("重试次数:", self.max_retry)
        ol.addLayout(fl2)
        ol.addStretch()
        layout.addWidget(opts_group)

        bl = QHBoxLayout()
        bl.setSpacing(12)
        self.start_btn = QPushButton("开始下载")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setMinimumWidth(120)
        self.start_btn.setObjectName("btnPrimary")
        self.start_btn.clicked.connect(self._on_start)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setMinimumWidth(80)
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

        log_group = QGroupBox("下载日志")
        ll = QVBoxLayout(log_group)
        ll.setContentsMargins(16, 20, 16, 16)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(120)
        self.log_text.setObjectName("logTerminal")
        ll.addWidget(self.log_text)
        layout.addWidget(log_group)

        self.scroll.setWidget(self.container)

    def update_theme(self, dark):
        pass

    @Slot()
    def _on_start(self):
        urls = self.url_input.toPlainText().strip().split("\n")
        urls = [u.strip() for u in urls if u.strip()]
        if not urls:
            self.log_text.append("[警告] 请输入至少一个链接")
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.start_btn.setEnabled(False)
        self.stop_btn.setObjectName("btnDangerActive")
        self.stop_btn.style().unpolish(self.stop_btn)
        self.stop_btn.style().polish(self.stop_btn)
        self.stop_btn.setEnabled(True)
        self.log_text.clear()
        self.log_text.append(f"[信息] 开始下载 {len(urls)} 个作品...")
        self._worker = DownloadWorker(self.bridge, self.async_thread, urls)
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
        self.stop_btn.setObjectName("btnDanger")
        self.stop_btn.style().unpolish(self.stop_btn)
        self.stop_btn.style().polish(self.stop_btn)
        self.log_text.append(f"[{'完成' if success else '错误'}] {msg}")
        self.progress_bar.setVisible(False)
        self._worker = None
        self.log_message.emit(msg)
