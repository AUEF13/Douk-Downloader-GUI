import json
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QCheckBox, QSpinBox, QComboBox, QFileDialog,
    QMessageBox, QScrollArea, QFrame, QCompleter,
)
from PySide6.QtCore import Qt, Signal, QThread
from ..theme import ThemeManager


class SettingsSaveWorker(QThread):
    finished = Signal(bool, str)
    def __init__(self, bridge, async_thread, settings):
        super().__init__()
        self.bridge = bridge
        self.async_thread = async_thread
        self.settings = settings
    def run(self):
        try:
            self.bridge.save_settings(self.settings)
            self.finished.emit(True, "设置已保存")
        except Exception as e:
            self.finished.emit(False, f"保存失败: {e}")


class SettingsPage(QWidget):
    settings_saved = Signal()
    KEYS = ["id", "desc", "create_time", "nickname", "uid", "mark", "type"]

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
        layout.setSpacing(20)

        self.header = QLabel("设置")
        hf = self.header.font()
        hf.setPointSize(18)
        hf.setBold(True)
        self.header.setFont(hf)
        layout.addWidget(self.header)

        stor_group = QGroupBox("存储设置")
        sl = QFormLayout(stor_group)
        sl.setSpacing(12)
        sl.setContentsMargins(16, 20, 16, 16)
        pr = QHBoxLayout()
        self.root_input = QLineEdit()
        self.root_input.setPlaceholderText("留空使用项目根目录")
        self.root_input.setMinimumWidth(300)
        self.root_input.setMinimumHeight(32)
        bb = QPushButton("浏览...")
        bb.setFixedWidth(80)
        bb.setMinimumHeight(32)
        bb.setObjectName("btnSecondary")
        bb.clicked.connect(lambda: (fp := QFileDialog.getExistingDirectory(self, "选择下载目录")) and self.root_input.setText(fp))
        pr.addWidget(self.root_input)
        pr.addWidget(bb)
        sl.addRow("下载路径:", pr)
        self.folder_name = QLineEdit("Download")
        self.folder_name.setMinimumHeight(32)
        sl.addRow("默认文件夹:", self.folder_name)
        sl.addRow(QCheckBox("按作品分文件夹保存"))
        sl.addRow(QCheckBox("下载音乐"))
        sl.addRow(QCheckBox("下载动态封面"))
        sl.addRow(QCheckBox("下载静态封面"))
        layout.addWidget(stor_group)

        name_group = QGroupBox("文件命名")
        nl = QFormLayout(name_group)
        nl.setSpacing(12)
        nl.setContentsMargins(16, 20, 16, 16)
        fr = QHBoxLayout()
        fr.setSpacing(8)
        self.name_format = QComboBox()
        self.name_format.setEditable(True)
        self.name_format.setMinimumHeight(32)
        self.name_format.setFrame(False)
        self.name_format.addItems(["create_time type nickname desc", "nickname create_time desc", "desc nickname"])
        self.name_format.setCurrentText("create_time type nickname desc")
        c = QCompleter(self.KEYS)
        c.setCaseSensitivity(Qt.CaseInsensitive)
        self.name_format.setCompleter(c)
        fr.addWidget(self.name_format, 1)
        hb = QPushButton("?")
        hb.setFixedSize(32, 32)
        hb.setObjectName("btnSecondary")
        hb.setToolTip("可用字段: id, desc, create_time, nickname, uid, mark, type\n用空格分隔")
        fr.addWidget(hb)
        nl.addRow("命名格式:", fr)
        nl.addRow("", QLabel("可用字段: id / desc / create_time / nickname / uid / mark / type（空格分隔）"))
        sr = QHBoxLayout()
        self.split = QLineEdit("-")
        self.split.setFixedWidth(60)
        self.split.setMinimumHeight(32)
        sr.addWidget(self.split)
        sr.addStretch()
        nl.addRow("分隔符:", sr)
        self.name_length = QSpinBox()
        self.name_length.setRange(32, 256)
        self.name_length.setValue(128)
        self.name_length.setMinimumHeight(32)
        nl.addRow("文件名最大长度:", self.name_length)
        self.desc_length = QSpinBox()
        self.desc_length.setRange(16, 128)
        self.desc_length.setValue(64)
        self.desc_length.setMinimumHeight(32)
        nl.addRow("描述最大长度:", self.desc_length)
        layout.addWidget(name_group)

        net_group = QGroupBox("网络设置")
        nn = QFormLayout(net_group)
        nn.setSpacing(12)
        nn.setContentsMargins(16, 20, 16, 16)
        self.proxy = QLineEdit()
        self.proxy.setPlaceholderText("http://127.0.0.1:7890 (留空不使用代理)")
        self.proxy.setMinimumHeight(32)
        nn.addRow("抖音代理:", self.proxy)
        self.proxy_tiktok = QLineEdit()
        self.proxy_tiktok.setPlaceholderText("http://127.0.0.1:7890 (留空不使用代理)")
        self.proxy_tiktok.setMinimumHeight(32)
        nn.addRow("TikTok代理:", self.proxy_tiktok)
        self.timeout = QSpinBox()
        self.timeout.setRange(2, 60)
        self.timeout.setValue(10)
        self.timeout.setSuffix(" 秒")
        self.timeout.setMinimumHeight(32)
        nn.addRow("请求超时:", self.timeout)
        self.max_retry = QSpinBox()
        self.max_retry.setRange(0, 10)
        self.max_retry.setValue(5)
        self.max_retry.setMinimumHeight(32)
        nn.addRow("最大重试:", self.max_retry)
        layout.addWidget(net_group)

        plat_group = QGroupBox("平台设置")
        pl = QFormLayout(plat_group)
        pl.setSpacing(12)
        pl.setContentsMargins(16, 20, 16, 16)
        pl.addRow(QCheckBox("启用抖音平台"))
        pl.addRow(QCheckBox("启用 TikTok 平台"))
        layout.addWidget(plat_group)

        self.save_frame = QFrame()
        self.save_frame.setObjectName("saveFrame")
        sfl = QHBoxLayout(self.save_frame)
        sfl.setContentsMargins(16, 12, 16, 12)
        self.save_btn = QPushButton("保存设置")
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
                if d.get("root"): self.root_input.setText(d["root"])
                if d.get("folder_name"): self.folder_name.setText(d["folder_name"])
                if d.get("name_format"): self.name_format.setCurrentText(d["name_format"])
                if d.get("split"): self.split.setText(d["split"])
                if d.get("name_length"): self.name_length.setValue(d["name_length"])
                if d.get("desc_length"): self.desc_length.setValue(d["desc_length"])
                if d.get("proxy"): self.proxy.setText(d["proxy"])
                if d.get("proxy_tiktok"): self.proxy_tiktok.setText(d["proxy_tiktok"])
                if d.get("timeout"): self.timeout.setValue(d["timeout"])
                if d.get("max_retry"): self.max_retry.setValue(d["max_retry"])
        except: pass

    def _on_save(self):
        settings = {
            "root": self.root_input.text().strip(),
            "folder_name": self.folder_name.text().strip() or "Download",
            "name_format": self.name_format.currentText().strip(),
            "split": self.split.text() or "-",
            "name_length": self.name_length.value(),
            "desc_length": self.desc_length.value(),
            "proxy": self.proxy.text().strip(),
            "proxy_tiktok": self.proxy_tiktok.text().strip(),
            "timeout": self.timeout.value(),
            "max_retry": self.max_retry.value(),
        }
        self.save_btn.setEnabled(False)
        self.status_label.setText("正在保存...")
        w = SettingsSaveWorker(self.bridge, self.async_thread, settings)
        w.finished.connect(self._on_done)
        w.start()

    def _on_done(self, ok, msg):
        self.save_btn.setEnabled(True)
        if ok:
            self.status_label.setText("设置已保存")
            self.settings_saved.emit()
        else:
            self.status_label.setText(f"保存失败: {msg}")
            self.status_label.setObjectName("statusError")
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
