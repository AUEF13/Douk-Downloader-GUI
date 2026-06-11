from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QCheckBox, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QTextCursor


class LogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        layout.setSpacing(12)

        self.header = QLabel("运行日志")
        h_font = self.header.font()
        h_font.setPointSize(18)
        h_font.setBold(True)
        self.header.setFont(h_font)
        layout.addWidget(self.header)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(16)
        self.auto_scroll = QCheckBox("自动滚动")
        self.auto_scroll.setChecked(True)
        toolbar.addWidget(self.auto_scroll)

        self.show_info = QCheckBox("信息")
        self.show_info.setChecked(True)
        self.show_info.stateChanged.connect(self._filter_logs)
        toolbar.addWidget(self.show_info)

        self.show_warning = QCheckBox("警告")
        self.show_warning.setChecked(True)
        self.show_warning.stateChanged.connect(self._filter_logs)
        toolbar.addWidget(self.show_warning)

        self.show_error = QCheckBox("错误")
        self.show_error.setChecked(True)
        self.show_error.stateChanged.connect(self._filter_logs)
        toolbar.addWidget(self.show_error)

        toolbar.addStretch()

        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.setMinimumHeight(32)
        self.clear_btn.setObjectName("btnSecondary")
        self.clear_btn.clicked.connect(self._clear_logs)
        toolbar.addWidget(self.clear_btn)

        layout.addLayout(toolbar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(400)
        self.log_text.setObjectName("logTerminal")
        layout.addWidget(self.log_text, 1)

        self.scroll.setWidget(self.container)

        self._all_lines: list[tuple[str, str]] = []

    def update_theme(self, dark):
        pass

    @Slot(str)
    def append_log(self, message: str, level: str = "info"):
        self._all_lines.append((message, level))
        if not self._should_show(level):
            return
        color_map = {"info": "#d4d4d4", "warning": "#dcdcaa", "error": "#f44747", "success": "#6a9955"}
        prefix_map = {"info": "[INFO]", "warning": "[WARN]", "error": "[ERROR]", "success": "[ OK ]"}
        color = color_map.get(level, "#d4d4d4")
        prefix = prefix_map.get(level, "[LOG]")
        self.log_text.append(f'<span style="color:{color};">{prefix} {message}</span>')
        if self.auto_scroll.isChecked():
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)

    def _should_show(self, level: str) -> bool:
        return {"info": self.show_info, "warning": self.show_warning, "error": self.show_error}.get(level, self.show_info).isChecked()

    def _filter_logs(self):
        self.log_text.clear()
        for msg, level in self._all_lines:
            if self._should_show(level):
                color_map = {"info": "#d4d4d4", "warning": "#dcdcaa", "error": "#f44747", "success": "#6a9955"}
                prefix_map = {"info": "[INFO]", "warning": "[WARN]", "error": "[ERROR]", "success": "[ OK ]"}
                color = color_map.get(level, "#d4d4d4")
                prefix = prefix_map.get(level, "[LOG]")
                self.log_text.append(f'<span style="color:{color};">{prefix} {msg}</span>')

    def _clear_logs(self):
        self._all_lines.clear()
        self.log_text.clear()
