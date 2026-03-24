from __future__ import annotations

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPen
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsSimpleTextItem

from src.domain.placed_piece import PlacedPiece


class PlacedBoxItem(QGraphicsRectItem):
    """Placed footprint: stroke 1.4px #4A4A4A, light fill; optional W×H label inside."""

    def __init__(self, piece: PlacedPiece) -> None:
        super().__init__(QRectF(0, 0, piece.width, piece.height))
        self.type_id = piece.type_id
        self._base_pen = QPen(QColor("#4A4A4A"))
        self._base_pen.setWidthF(1.4)
        self._base_pen.setCosmetic(True)
        self._active_pen = QPen(QColor("#1F2326"))
        self._active_pen.setWidthF(2.0)
        self._active_pen.setCosmetic(True)
        self._hover_pen = QPen(QColor("#2E3539"))
        self._hover_pen.setWidthF(1.8)
        self._hover_pen.setCosmetic(True)
        self._is_selected = False
        self._is_hovered = False

        self.setPos(piece.x, piece.y)
        palette = (
            "#E6E8E3",
            "#E3E8EA",
            "#E8E5DF",
            "#E2E7E1",
            "#E7E3E8",
            "#E6E4DF",
            "#E2E6E7",
        )
        c = QColor(palette[piece.type_id % len(palette)])
        c.setAlphaF(0.92)
        self._base_brush = QBrush(c)
        self._active_brush = QBrush(c.lighter(92))
        self._hover_brush = QBrush(c.lighter(96))
        self.setBrush(self._base_brush)
        self.setPen(self._base_pen)
        self.setZValue(10)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)

        # Dimension text inside box when large enough (scene units = mm)
        min_mm = 80.0
        if piece.width >= min_mm and piece.height >= min_mm:
            label = f"T{piece.type_id + 1}  {int(piece.width)} x {int(piece.height)}"
            t = QGraphicsSimpleTextItem(label, self)
            t.setBrush(QColor("#444A4F"))
            f = QFont("Inter", 9)
            t.setFont(f)
            br = t.boundingRect()
            cx = (piece.width - br.width()) / 2
            cy = (piece.height - br.height()) / 2
            t.setPos(cx, cy)
            t.setZValue(20)

    def set_selected_visual(self, selected: bool) -> None:
        self._is_selected = selected
        self._apply_state_style()

    def set_hover_visual(self, hovered: bool) -> None:
        self._is_hovered = hovered
        self._apply_state_style()

    def _apply_state_style(self) -> None:
        if self._is_selected:
            self.setPen(self._active_pen)
            self.setBrush(self._active_brush)
            return
        if self._is_hovered:
            self.setPen(self._hover_pen)
            self.setBrush(self._hover_brush)
            return
        self.setPen(self._base_pen)
        self.setBrush(self._base_brush)
