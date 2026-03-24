from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractSpinBox,
    QAbstractItemView,
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class BinItemTable(QWidget):
    """Editable table: w, h, q, rotation per row."""

    changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["w (mm)", "h (mm)", "qty", "90° rot."])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self._table.setColumnWidth(2, 96)
        self._table.setColumnWidth(3, 110)
        self._table.verticalHeader().setDefaultSectionSize(42)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setMinimumSectionSize(72)
        self._table.verticalHeader().setDefaultAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self._table.itemChanged.connect(lambda *_: self.changed.emit())

        btn_add = QPushButton("Add type")
        btn_add.setObjectName("btnSecondary")
        btn_add.clicked.connect(self.add_row)
        btn_rem = QPushButton("Remove selected")
        btn_rem.setObjectName("btnSecondary")
        btn_rem.clicked.connect(self._remove_row)

        row = QHBoxLayout()
        row.addWidget(btn_add)
        row.addWidget(btn_rem)
        row.addStretch(1)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._table)
        lay.addLayout(row)

        self.add_row()

    def add_row(self) -> None:
        r = self._table.rowCount()
        self._table.insertRow(r)
        for c, val in enumerate((200.0, 150.0, 1, False)):
            if c < 2:
                spin = QDoubleSpinBox()
                spin.setRange(0.01, 1e9)
                spin.setDecimals(2)
                spin.setValue(float(val))
                spin.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
                spin.setKeyboardTracking(False)
                spin.valueChanged.connect(lambda *_: self.changed.emit())
                self._table.setCellWidget(r, c, spin)
            elif c == 2:
                iq = QSpinBox()
                iq.setRange(0, 1_000_000)
                iq.setValue(int(val))
                iq.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                iq.setButtonSymbols(QAbstractSpinBox.NoButtons)
                iq.setKeyboardTracking(False)
                iq.valueChanged.connect(lambda *_: self.changed.emit())
                self._table.setCellWidget(r, c, iq)
            else:
                cb = QCheckBox()
                cb.setChecked(bool(val))
                cb.stateChanged.connect(lambda *_: self.changed.emit())
                cb_wrap = QWidget()
                cb_lay = QHBoxLayout(cb_wrap)
                cb_lay.setContentsMargins(0, 0, 0, 0)
                cb_lay.setAlignment(Qt.AlignCenter)
                cb_lay.addWidget(cb)
                self._table.setCellWidget(r, c, cb_wrap)
        self.changed.emit()

    def _remove_row(self) -> None:
        r = self._table.currentRow()
        if r >= 0:
            self._table.removeRow(r)
            if self._table.rowCount() == 0:
                self.add_row()
            self.changed.emit()

    def load_items(self, items: list[dict]) -> None:
        while self._table.rowCount():
            self._table.removeRow(0)
        if not items:
            self.add_row()
            return
        for _ in items:
            self.add_row()
        for row, it in enumerate(items):
            w = self._table.cellWidget(row, 0)
            h = self._table.cellWidget(row, 1)
            q = self._table.cellWidget(row, 2)
            rot = self._table.cellWidget(row, 3)
            assert isinstance(w, QDoubleSpinBox)
            assert isinstance(h, QDoubleSpinBox)
            assert isinstance(q, QSpinBox)
            assert isinstance(rot, QCheckBox)
            w.setValue(float(it["w"]))
            h.setValue(float(it["h"]))
            q.setValue(int(it["q"]))
            rot.setChecked(bool(it.get("rotation", False)))
        self.changed.emit()

    def to_items_payload(self) -> list[dict]:
        out: list[dict] = []
        for row in range(self._table.rowCount()):
            w = self._table.cellWidget(row, 0)
            h = self._table.cellWidget(row, 1)
            q = self._table.cellWidget(row, 2)
            rot = self._table.cellWidget(row, 3)
            assert isinstance(w, QDoubleSpinBox)
            assert isinstance(h, QDoubleSpinBox)
            assert isinstance(q, QSpinBox)
            assert isinstance(rot, QCheckBox)
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
