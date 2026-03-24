from __future__ import annotations

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QGraphicsRectItem


class BinOutlineItem(QGraphicsRectItem):
    """Pallet outline: 2px stroke #2F2F2F, light fill."""

    def __init__(self, width: float, height: float) -> None:
        super().__init__(QRectF(0, 0, width, height))
        pen = QPen(QColor("#3B3F42"))
        pen.setWidthF(2.0)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(QBrush(QColor("#F7F8F5")))
        self.setZValue(0)
