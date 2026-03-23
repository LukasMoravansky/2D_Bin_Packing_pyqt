from __future__ import annotations

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsView


class PackingGraphicsView(QGraphicsView):
    """View for technical drawing canvas; uniform scale, antialiasing."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRenderHints(
            QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(Qt.transparent)
        self.setFrameShape(QGraphicsView.NoFrame)

    def fit_bin(self, bin_w: float, bin_h: float) -> None:
        self.resetTransform()
        self.fitInView(QRectF(0, 0, bin_w, bin_h), Qt.KeepAspectRatio)
