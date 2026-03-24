from __future__ import annotations

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsScene

from src.domain.bin_spec import BinSpec
from src.domain.solution import PackingSolution
from App.graphics.items.bin_item import BinOutlineItem
from App.graphics.items.box_item import PlacedBoxItem


class PackingScene(QGraphicsScene):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._bin_item: BinOutlineItem | None = None

    def clear_scene(self) -> None:
        self.clear()
        self.setSceneRect(QRectF())
        self._bin_item = None

    def draw_solution(self, bin_spec: BinSpec, solution: PackingSolution | None) -> None:
        self.clear()
        self.setSceneRect(QRectF(0, 0, bin_spec.width, bin_spec.height))
        self._bin_item = BinOutlineItem(bin_spec.width, bin_spec.height)
        self.addItem(self._bin_item)

        # Optional grid (very light) — behind bin
        grid_pen = QPen(QColor("#E8EAE6"))
        grid_pen.setWidthF(0.5)
        grid_pen.setCosmetic(True)
        step = max(bin_spec.width, bin_spec.height) / 10.0
        if step > 1:
            x = 0.0
            while x <= bin_spec.width:
                self.addLine(x, 0, x, bin_spec.height, grid_pen).setZValue(-5)
                x += step
            y = 0.0
            while y <= bin_spec.height:
                self.addLine(0, y, bin_spec.width, y, grid_pen).setZValue(-5)
                y += step

        if solution is None:
            return
        for p in solution.placed:
            self.addItem(PlacedBoxItem(p))
