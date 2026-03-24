from __future__ import annotations

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QGraphicsView


class PackingGraphicsView(QGraphicsView):
    """View for technical drawing canvas; uniform scale, antialiasing."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._target_rect: QRectF | None = None
        self.setObjectName("packingView")
        self.setRenderHints(
            QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QColor("#ECEEEA"))
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setMouseTracking(True)

    def fit_bin(self, bin_w: float, bin_h: float) -> None:
        self._target_rect = QRectF(0, 0, bin_w, bin_h)
        self._fit_target_rect()

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        super().resizeEvent(event)
        self._fit_target_rect()

    def _fit_target_rect(self) -> None:
        if self._target_rect is None:
            return
        if self.viewport().width() <= 0 or self.viewport().height() <= 0:
            return
        self.resetTransform()
        self.fitInView(self._target_rect, Qt.KeepAspectRatio)
