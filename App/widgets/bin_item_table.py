from __future__ import annotations

from PyQt5.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractSpinBox,
    QAbstractItemView,
    QAbstractScrollArea,
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class BinItemTable(QWidget):
    """Editable table: w, h, q, rotation per row."""

    changed = pyqtSignal()
    selection_changed = pyqtSignal(int)
    hover_changed = pyqtSignal(int)
    _SPINBOX_V_MARGIN = 4
    _SPINBOX_H_MARGIN = 6
    _ROW_HEIGHT_BUFFER = 2
    _QTY_COL_WIDTH = 88
    _ROT_COL_WIDTH = 112

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._editor_min_height = self._compute_editor_min_height()
        self._ROW_HEIGHT = (
            self._editor_min_height + (2 * self._SPINBOX_V_MARGIN) + self._ROW_HEIGHT_BUFFER
        )
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["w (mm)", "h (mm)", "qty", "90° rot."])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self._table.setColumnWidth(2, self._QTY_COL_WIDTH)
        self._table.setColumnWidth(3, self._ROT_COL_WIDTH)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.horizontalHeader().setMinimumSectionSize(64)
        self._table.verticalHeader().setDefaultSectionSize(self._ROW_HEIGHT)
        self._table.verticalHeader().setMinimumSectionSize(self._ROW_HEIGHT)
        self._table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self._table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setMouseTracking(True)
        self._table.verticalHeader().setDefaultAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self._table.itemChanged.connect(lambda *_: self.changed.emit())
        self._table.itemSelectionChanged.connect(self._emit_selection_changed)
        self._table.cellEntered.connect(self._on_cell_entered)
        self._table.viewport().installEventFilter(self)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._table)

        self._apply_minimum_heights()
        self.add_row()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._table.viewport() and event.type() == QEvent.Leave:
            self.hover_changed.emit(-1)
        if isinstance(watched, QAbstractSpinBox) and event.type() == QEvent.Wheel:
            # Prevent accidental value changes while scrolling over table inputs.
            event.ignore()
            return True
        return super().eventFilter(watched, event)

    def add_row(self) -> None:
        r = self._table.rowCount()
        self._table.insertRow(r)
        self._table.setRowHeight(r, self._ROW_HEIGHT)
        for c, val in enumerate((200.0, 150.0, 1, False)):
            if c < 2:
                spin = QDoubleSpinBox()
                spin.setRange(0.01, 1e9)
                spin.setDecimals(2)
                spin.setValue(float(val))
                spin.setMinimumHeight(self._editor_min_height)
                spin.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
                spin.setKeyboardTracking(False)
                spin.installEventFilter(self)
                spin.valueChanged.connect(lambda *_: self.changed.emit())
                self._table.setCellWidget(r, c, self._wrap_cell_widget(spin))
            elif c == 2:
                iq = QSpinBox()
                iq.setRange(0, 1_000_000)
                iq.setValue(int(val))
                iq.setMinimumHeight(self._editor_min_height)
                iq.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                iq.setButtonSymbols(QAbstractSpinBox.NoButtons)
                iq.setKeyboardTracking(False)
                iq.installEventFilter(self)
                iq.valueChanged.connect(lambda *_: self.changed.emit())
                self._table.setCellWidget(r, c, self._wrap_cell_widget(iq))
            else:
                cb = QCheckBox()
                cb.setChecked(bool(val))
                cb.stateChanged.connect(lambda *_: self.changed.emit())
                cb_wrap = QWidget()
                cb_lay = QHBoxLayout(cb_wrap)
                cb_lay.setContentsMargins(0, 0, 0, 0)
                cb_lay.setSpacing(0)
                cb_lay.setAlignment(Qt.AlignCenter)
                cb_lay.addWidget(cb)
                self._table.setCellWidget(r, c, cb_wrap)
        self.changed.emit()

    @staticmethod
    def _wrap_cell_widget(widget: QWidget) -> QWidget:
        wrap = QWidget()
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(
            BinItemTable._SPINBOX_H_MARGIN,
            BinItemTable._SPINBOX_V_MARGIN,
            BinItemTable._SPINBOX_H_MARGIN,
            BinItemTable._SPINBOX_V_MARGIN,
        )
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignVCenter)
        lay.addWidget(widget)
        return wrap

    @staticmethod
    def _compute_editor_min_height() -> int:
        probe = QDoubleSpinBox()
        probe.setButtonSymbols(QAbstractSpinBox.NoButtons)
        # Respect active style metrics so editors never get clipped.
        return max(30, probe.sizeHint().height())

    def remove_selected_row(self) -> None:
        r = self._table.currentRow()
        if r >= 0:
            self._table.removeRow(r)
            if self._table.rowCount() == 0:
                self.add_row()
            self.changed.emit()
            self._emit_selection_changed()

    def _apply_minimum_heights(self) -> None:
        header_h = self._table.horizontalHeader().sizeHint().height()
        table_min_h = header_h + self._ROW_HEIGHT + 8
        self._table.setMinimumHeight(table_min_h)
        self.setMinimumHeight(table_min_h)

    def selected_type_id(self) -> int:
        row = self._table.currentRow()
        if row < 0:
            return -1
        return row

    def select_type_id(self, type_id: int) -> None:
        if 0 <= type_id < self._table.rowCount():
            self._table.selectRow(type_id)
            idx = self._table.model().index(type_id, 0)
            self._table.scrollTo(idx, QAbstractItemView.PositionAtCenter)
            self._emit_selection_changed()

    def load_items(self, items: list[dict]) -> None:
        while self._table.rowCount():
            self._table.removeRow(0)
        if not items:
            self.add_row()
            return
        for _ in items:
            self.add_row()
        for row, it in enumerate(items):
            w = self._get_cell_spinbox(row, 0, QDoubleSpinBox)
            h = self._get_cell_spinbox(row, 1, QDoubleSpinBox)
            q = self._get_cell_spinbox(row, 2, QSpinBox)
            rot = self._get_rotation_checkbox(row)
            w.setValue(float(it["w"]))
            h.setValue(float(it["h"]))
            q.setValue(int(it["q"]))
            rot.setChecked(bool(it.get("rotation", False)))
        self.changed.emit()
        self._emit_selection_changed()

    def to_items_payload(self) -> list[dict]:
        out: list[dict] = []
        for row in range(self._table.rowCount()):
            w = self._get_cell_spinbox(row, 0, QDoubleSpinBox)
            h = self._get_cell_spinbox(row, 1, QDoubleSpinBox)
            q = self._get_cell_spinbox(row, 2, QSpinBox)
            rot = self._get_rotation_checkbox(row)
            out.append(
                {
                    "id": row,
                    "w": w.value(),
                    "h": h.value(),
                    "q": q.value(),
                    "rotation": rot.isChecked(),
                }
            )
        return out

    def _get_cell_spinbox(self, row: int, col: int, expected_type):
        wrap = self._table.cellWidget(row, col)
        assert isinstance(wrap, QWidget)
        child = wrap.findChild(expected_type)
        assert child is not None
        return child

    def _get_rotation_checkbox(self, row: int) -> QCheckBox:
        wrap = self._table.cellWidget(row, 3)
        assert isinstance(wrap, QWidget)
        child = wrap.findChild(QCheckBox)
        assert child is not None
        return child

    def _emit_selection_changed(self) -> None:
        self.selection_changed.emit(self.selected_type_id())

    def _on_cell_entered(self, row: int, _col: int) -> None:
        self.hover_changed.emit(row)
