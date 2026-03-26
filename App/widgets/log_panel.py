from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class LogPanel(QWidget):
    """System log with Clear button; append via append_line from main thread."""

    clear_clicked = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        title = QLabel("System log")
        title.setObjectName("sectionTitle")
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setObjectName("logPlainText")
        self._text.setMinimumHeight(120)
        btn_clear = QPushButton("Clear Logger")
        btn_clear.setObjectName("btnSecondary")
        btn_clear.setMinimumWidth(128)
        btn_clear.clicked.connect(self._on_clear)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        row.setAlignment(Qt.AlignVCenter)
        row.addWidget(title)
        row.addStretch(1)
        row.addWidget(btn_clear)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 14, 20, 20)
        lay.setSpacing(12)
        lay.addLayout(row)
        lay.addWidget(self._text)

    def _on_clear(self) -> None:
        self._text.clear()
        self.clear_clicked.emit()

    def append_line(self, line: str) -> None:
        self._text.appendPlainText(line)
