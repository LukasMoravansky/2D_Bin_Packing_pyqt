from __future__ import annotations

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPen
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsSimpleTextItem

from src.domain.placed_piece import PlacedPiece


class PlacedBoxItem(QGraphicsRectItem):
    """Placed footprint: stroke 1.4px #4A4A4A, light fill; optional W×H label inside."""

    def __init__(self, piece: PlacedPiece) -> None:
        super().__init__(QRectF(0, 0, piece.width, piece.height))
        self.setPos(piece.x, piece.y)
        pen = QPen(QColor("#5A5F63"))
        pen.setWidthF(1.4)
        pen.setCosmetic(True)
        self.setPen(pen)
        c = QColor("#F1F3EE")
        c.setAlphaF(0.92)
        self.setBrush(QBrush(c))
        self.setZValue(10)

        # Dimension text inside box when large enough (scene units = mm)
        min_mm = 80.0
        if piece.width >= min_mm and piece.height >= min_mm:
            label = f"{int(piece.width)} x {int(piece.height)}"
            t = QGraphicsSimpleTextItem(label, self)
            t.setBrush(QColor("#444A4F"))
            f = QFont("Inter", 9)
            t.setFont(f)
            br = t.boundingRect()
            cx = (piece.width - br.width()) / 2
            cy = (piece.height - br.height()) / 2
            t.setPos(cx, cy)
            t.setZValue(20)
