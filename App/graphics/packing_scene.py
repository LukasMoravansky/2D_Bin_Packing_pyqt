from __future__ import annotations

from PyQt5.QtCore import QRectF, pyqtSignal
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsScene

from src.domain.bin_spec import BinSpec
from src.domain.solution import PackingSolution
from App.graphics.items.bin_item import BinOutlineItem
from App.graphics.items.box_item import PlacedBoxItem


class PackingScene(QGraphicsScene):
    box_clicked = pyqtSignal(int)
    box_hovered = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._bin_item: BinOutlineItem | None = None
        self._box_items: list[PlacedBoxItem] = []

    def clear_scene(self) -> None:
        self.clear()
        self.setSceneRect(QRectF())
        self._bin_item = None
        self._box_items = []

    def draw_solution(self, bin_spec: BinSpec, solution: PackingSolution | None) -> None:
        self.clear()
        self.setSceneRect(QRectF(0, 0, bin_spec.width, bin_spec.height))
        self._bin_item = BinOutlineItem(bin_spec.width, bin_spec.height)
        self.addItem(self._bin_item)
        self._box_items = []

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
            box = PlacedBoxItem(p)
            self.addItem(box)
            self._box_items.append(box)

    def highlight_type(self, type_id: int, mode: str = "selected") -> None:
        for box in self._box_items:
            if mode == "selected":
                box.set_selected_visual(box.type_id == type_id and type_id >= 0)
                box.set_hover_visual(False)
            else:
                box.set_hover_visual(box.type_id == type_id and type_id >= 0)

    def clear_highlight(self) -> None:
        for box in self._box_items:
            box.set_selected_visual(False)
            box.set_hover_visual(False)

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        item = self.itemAt(event.scenePos(), self.views()[0].transform()) if self.views() else None
        if isinstance(item, PlacedBoxItem):
            self.box_clicked.emit(item.type_id)
            self.highlight_type(item.type_id, mode="selected")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        item = self.itemAt(event.scenePos(), self.views()[0].transform()) if self.views() else None
        if isinstance(item, PlacedBoxItem):
            self.box_hovered.emit(item.type_id)
            self.highlight_type(item.type_id, mode="hover")
        else:
            self.box_hovered.emit(-1)
            self.highlight_type(-1, mode="hover")
        super().mouseMoveEvent(event)
