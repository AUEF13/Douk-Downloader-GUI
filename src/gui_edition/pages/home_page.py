import json
import random
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QFont, QPixmap

from ..theme import ThemeManager


LOCAL_QUOTES = [
    ("我们走得太快，灵魂都跟不上了。", "沃尔特·惠特曼"),
    ("生活不止眼前的苟且，还有诗和远方的田野。", "高晓松"),
    ("世界上只有一种真正的英雄主义，那就是在认清生活的真相后依然热爱生活。", "罗曼·罗兰"),
    ("你不能等待别人来安排你的人生；自己想要的，自己争取。", "宫崎骏"),
    ("不乱于心，不困于情，不畏将来，不念过往。如此，安好。", "丰子恺"),
    ("人生如逆旅，我亦是行人。", "苏轼"),
    ("山有木兮木有枝，心悦君兮君不知。", "《越人歌》"),
    ("采菊东篱下，悠然见南山。", "陶渊明"),
    ("路漫漫其修远兮，吾将上下而求索。", "屈原"),
    ("海纳百川，有容乃大。", "林则徐"),
    ("千里之行，始于足下。", "老子"),
    ("学而不思则罔，思而不学则殆。", "孔子"),
    ("己所不欲，勿施于人。", "孔子"),
    ("三人行，必有我师焉。", "孔子"),
    ("天行健，君子以自强不息。", "《周易》"),
    ("知者不惑，仁者不忧，勇者不惧。", "孔子"),
    ("工欲善其事，必先利其器。", "孔子"),
    ("逝者如斯夫，不舍昼夜。", "孔子"),
    ("吾日三省吾身。", "曾子"),
    ("生于忧患，死于安乐。", "孟子"),
]


class HitokotoWorker(QThread):
    finished = Signal(str, str)

    def run(self):
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://v1.hitokoto.cn/?c=d&c=h&c=i&c=k",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data.get("hitokoto", "")
                source = data.get("from", "")
                self.finished.emit(text, source)
        except Exception:
            text, source = random.choice(LOCAL_QUOTES)
            self.finished.emit(text, source)


class HomePage(QWidget):
    navigate = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = False
        self._setup_ui()
        self._load_hitokoto()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        layout.addStretch()

        self.logo_label = QLabel()
        logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            self.logo_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.logo_label)

        layout.addSpacing(20)

        self.quote_label = QLabel("...")
        self.quote_label.setAlignment(Qt.AlignCenter)
        self.quote_label.setWordWrap(False)
        qf = QFont("MiSans", 16)
        qf.setBold(True)
        self.quote_label.setFont(qf)
        self.quote_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.quote_label)

        self.source_label = QLabel("")
        self.source_label.setAlignment(Qt.AlignCenter)
        sf = QFont("MiSans", 11)
        self.source_label.setFont(sf)
        self.source_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.source_label)

        layout.addStretch()

        self._worker = None

    def _load_hitokoto(self):
        self._worker = HitokotoWorker()
        self._worker.finished.connect(self._on_hitokoto)
        self._worker.start()

    @Slot(str, str)
    def _on_hitokoto(self, text: str, source: str):
        self.quote_label.setText(f"\u201c{text}\u201d")
        if source:
            self.source_label.setText(f"—— {source}")
        else:
            self.source_label.setText("")

    def update_theme(self, dark: bool):
        self._dark = dark
        if dark:
            self.quote_label.setStyleSheet("color: #e0e0e0; background: transparent;")
            self.source_label.setStyleSheet("color: #888; background: transparent;")
            self.version_label.setStyleSheet("color: #555; background: transparent;")
        else:
            self.quote_label.setStyleSheet("color: #2c3e50; background: transparent;")
            self.source_label.setStyleSheet("color: #888; background: transparent;")
            self.version_label.setStyleSheet("color: #aaa; background: transparent;")
