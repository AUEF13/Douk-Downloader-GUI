import json
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QGroupBox,
    QFrame, QMessageBox, QApplication, QFileDialog, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QThread
from ..theme import ThemeManager


class CookieSaveWorker(QThread):
    finished = Signal(bool, str)
    def __init__(self, bridge, async_thread, cookie, cookie_tiktok):
        super().__init__()
        self.bridge = bridge
        self.async_thread = async_thread
        self.cookie = cookie
        self.cookie_tiktok = cookie_tiktok
    def run(self):
        try:
            f = self.async_thread.run_coro(self.bridge.update_cookie(self.cookie, self.cookie_tiktok))
            if f: f.result(timeout=30)
            self.bridge.save_cookies(self.cookie, self.cookie_tiktok)
            self.finished.emit(True, "Cookie 保存成功")
        except Exception as e:
            self.finished.emit(False, f"保存失败: {e}")


class CookiePage(QWidget):
    cookie_updated = Signal()
    def __init__(self, bridge=None, async_thread=None, parent=None):
        super().__init__(parent)
        self.bridge = bridge
        self.async_thread = async_thread
        self._setup_ui()
        self._load_existing()

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

        self.header = QLabel("Cookie 管理")
        hf = self.header.font()
        hf.setPointSize(18)
        hf.setBold(True)
        self.header.setFont(hf)
        layout.addWidget(self.header)

        self.hint = QLabel("Cookie 用于访问抖音/TikTok 的数据接口。\n获取方式: 在浏览器中登录，打开开发者工具(F12)，在 Application > Cookies 中复制完整 Cookie。")
        self.hint.setWordWrap(True)
        self.hint.setObjectName("hintBox")
        layout.addWidget(self.hint)

        dy_group = QGroupBox("抖音 Cookie")
        dl = QVBoxLayout(dy_group)
        dl.setSpacing(8)
        dl.setContentsMargins(16, 20, 16, 16)
        self.douyin_cookie = QTextEdit()
        self.douyin_cookie.setPlaceholderText("粘贴抖音 Cookie 字符串...")
        self.douyin_cookie.setMaximumHeight(100)
        dl.addWidget(self.douyin_cookie)
        db = QHBoxLayout()
        db.setSpacing(8)
        for text, conn in [("从剪贴板粘贴", lambda: self.douyin_cookie.setPlainText(QApplication.clipboard().text())),
                           ("从文件读取", lambda: self._load_from_file(self.douyin_cookie)),
                           ("清空", lambda: self.douyin_cookie.clear())]:
            b = QPushButton(text)
            b.setMinimumHeight(32)
            b.setObjectName("btnSecondary")
            b.clicked.connect(conn)
            db.addWidget(b)
        db.addStretch()
        dl.addLayout(db)
        layout.addWidget(dy_group)

        tk_group = QGroupBox("TikTok Cookie")
        tl = QVBoxLayout(tk_group)
        tl.setSpacing(8)
        tl.setContentsMargins(16, 20, 16, 16)
        self.tiktok_cookie = QTextEdit()
        self.tiktok_cookie.setPlaceholderText("粘贴 TikTok Cookie 字符串...")
        self.tiktok_cookie.setMaximumHeight(100)
        tl.addWidget(self.tiktok_cookie)
        tb = QHBoxLayout()
        tb.setSpacing(8)
        for text, conn in [("从剪贴板粘贴", lambda: self.tiktok_cookie.setPlainText(QApplication.clipboard().text())),
                           ("从文件读取", lambda: self._load_from_file(self.tiktok_cookie)),
                           ("清空", lambda: self.tiktok_cookie.clear())]:
            b = QPushButton(text)
            b.setMinimumHeight(32)
            b.setObjectName("btnSecondary")
            b.clicked.connect(conn)
            tb.addWidget(b)
        tb.addStretch()
        tl.addLayout(tb)
        layout.addWidget(tk_group)

        self.save_frame = QFrame()
        self.save_frame.setObjectName("saveFrame")
        sfl = QHBoxLayout(self.save_frame)
        sfl.setContentsMargins(16, 12, 16, 12)
        self.save_btn = QPushButton("保存 Cookie")
        self.save_btn.setFixedSize(140, 40)
        self.save_btn.setObjectName("btnAction")
        self.save_btn.clicked.connect(self._on_save)
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusOk")
        sfl.addWidget(self.save_btn)
        sfl.addWidget(self.status_label)
        sfl.addStretch()
        layout.addWidget(self.save_frame)
        layout.addStretch()
        self.scroll.setWidget(self.container)

    def update_theme(self, dark):
        pass

    def _load_existing(self):
        try:
            p = Path(__file__).parent.parent.parent.parent / "settings.json"
            if p.exists():
                d = json.loads(p.read_text("utf-8-sig"))
                if d.get("cookie"): self.douyin_cookie.setPlainText(d["cookie"])
                if d.get("cookie_tiktok"): self.tiktok_cookie.setPlainText(d["cookie_tiktok"])
        except: pass

    def _load_from_file(self, target):
        fp, _ = QFileDialog.getOpenFileName(self, "选择 Cookie 文件", "", "文本文件 (*.txt);;所有文件 (*.*)")
        if fp:
            try: target.setPlainText(Path(fp).read_text("utf-8").strip())
            except Exception as e: QMessageBox.warning(self, "读取失败", str(e))

    def _on_save(self):
        dy = self.douyin_cookie.toPlainText().strip()
        tk = self.tiktok_cookie.toPlainText().strip()
        if not dy and not tk:
            QMessageBox.warning(self, "提示", "请至少填写一个 Cookie")
            return
        self.save_btn.setEnabled(False)
        self.status_label.setText("正在保存...")
        w = CookieSaveWorker(self.bridge, self.async_thread, dy, tk)
        w.finished.connect(self._on_done)
        w.start()

    def _on_done(self, ok, msg):
        self.save_btn.setEnabled(True)
        if ok:
            self.status_label.setText("Cookie 已保存并生效")
            self.cookie_updated.emit()
        else:
            self.status_label.setText(f"保存失败: {msg}")
            self.status_label.setObjectName("statusError")
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
