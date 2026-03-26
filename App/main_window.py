from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QDoubleSpinBox,
)

from App.app_logging import configure_logging, get_logger
from App.graphics.packing_scene import PackingScene
from App.graphics.packing_view import PackingGraphicsView
from App.widgets.bin_item_table import BinItemTable
from App.widgets.log_panel import LogPanel
from App.widgets.styled_frame import StyledFrame
from App.workers.solve_worker import SolveThread
from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.io.json_config import load_problem_from_json_file, save_problem_to_json_file
from src.validation.input_model import build_problem_from_dict
from src.validation.validate import validate

_LOG = get_logger("packing.gui")


class _LogEmitter(QObject):
    line = pyqtSignal(str)


class MainWindow(QMainWindow):
    _LEFT_NON_SPLITTER_RESERVED_HEIGHT = 110

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("2D Single-Bin Packing — Benchmark")
        self._solve_thread: SolveThread | None = None
        self._last_solution: PackingSolution | None = None
        self._scenario_name = "Manual scenario"

        central = QWidget()
        central.setObjectName("appRoot")
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(16)

        title = QLabel("2D palletization")
        title.setObjectName("pageTitle")
        outer.addWidget(title)

        self._status_bar = QWidget()
        self._status_bar.setObjectName("statusBarSurface")
        status_lay = QHBoxLayout(self._status_bar)
        status_lay.setContentsMargins(14, 10, 14, 10)
        status_lay.setSpacing(12)
        self._scenario_label = QLabel(f"Scenario: {self._scenario_name}")
        self._scenario_label.setObjectName("statusScenario")
        self._state_badge = QLabel("INVALID")
        self._state_badge.setObjectName("statusBadgeInvalid")
        self._last_run_label = QLabel("Last run: —")
        self._last_run_label.setObjectName("statusTimestamp")
        status_lay.addWidget(self._scenario_label)
        status_lay.addWidget(self._state_badge)
        status_lay.addStretch(1)
        status_lay.addWidget(self._last_run_label)
        outer.addWidget(self._status_bar)

        split_v = QSplitter(Qt.Vertical)
        split_h = QSplitter(Qt.Horizontal)

        # Left: inputs
        left = StyledFrame()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(20, 20, 20, 20)
        left_lay.setSpacing(16)

        bin_title = QLabel("Pallet (bin)")
        bin_title.setObjectName("cardTitle")
        left_lay.addWidget(bin_title)

        form = QFormLayout()
        self._spin_w = QDoubleSpinBox()
        self._spin_h = QDoubleSpinBox()
        self._spin_g = QDoubleSpinBox()
        for sp in (self._spin_w, self._spin_h, self._spin_g):
            sp.setRange(0.0, 1e9)
            sp.setDecimals(2)
            sp.installEventFilter(self)
        self._spin_w.setValue(1200.0)
        self._spin_h.setValue(800.0)
        self._spin_g.setValue(5.0)
        self._spin_w.valueChanged.connect(self._on_inputs_changed)
        self._spin_h.valueChanged.connect(self._on_inputs_changed)
        self._spin_g.valueChanged.connect(self._on_inputs_changed)
        form.addRow("W (mm)", self._spin_w)
        form.addRow("H (mm)", self._spin_h)
        form.addRow("g (mm)", self._spin_g)
        left_lay.addLayout(form)

        items_title = QLabel("Item types")
        items_title.setObjectName("cardTitle")
        left_lay.addWidget(items_title)

        self._item_split = QSplitter(Qt.Vertical)
        self._item_split.setChildrenCollapsible(False)
        self._item_split.setHandleWidth(6)

        table_section = QWidget()
        table_section_lay = QVBoxLayout(table_section)
        table_section_lay.setContentsMargins(0, 0, 0, 0)
        table_section_lay.setSpacing(0)
        self._table = BinItemTable()
        self._table.changed.connect(self._on_inputs_changed)
        table_section_lay.addWidget(self._table)

        controls_section = QWidget()
        controls_lay = QVBoxLayout(controls_section)
        controls_lay.setContentsMargins(0, 8, 0, 0)
        controls_lay.setSpacing(10)

        item_btn_row = QHBoxLayout()
        item_btn_row.setSpacing(12)
        item_btn_row.setContentsMargins(0, 0, 0, 0)
        btn_add_type = QPushButton("Add type")
        btn_add_type.setObjectName("btnSecondary")
        btn_add_type.setMinimumWidth(112)
        btn_add_type.clicked.connect(self._table.add_row)
        btn_remove_type = QPushButton("Remove selected")
        btn_remove_type.setObjectName("btnSecondary")
        btn_remove_type.setMinimumWidth(146)
        btn_remove_type.clicked.connect(self._table.remove_selected_row)
        item_btn_row.addWidget(btn_add_type)
        item_btn_row.addWidget(btn_remove_type)
        item_btn_row.addStretch(1)
        controls_lay.addLayout(item_btn_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.setContentsMargins(0, 0, 0, 0)
        self._btn_run = QPushButton("Run")
        self._btn_run.setObjectName("btnPrimary")
        self._btn_run.setMinimumHeight(40)
        self._btn_run.clicked.connect(self._on_run)
        self._btn_reset = QPushButton("Reset Scene")
        self._btn_reset.setObjectName("btnSecondary")
        self._btn_reset.setMinimumHeight(40)
        self._btn_reset.clicked.connect(self._on_reset_scene)
        self._btn_load = QPushButton("Load JSON…")
        self._btn_load.setObjectName("btnSecondary")
        self._btn_load.setMinimumHeight(40)
        self._btn_load.clicked.connect(self._on_load_json)
        self._btn_save = QPushButton("Save JSON…")
        self._btn_save.setObjectName("btnSecondary")
        self._btn_save.setMinimumHeight(40)
        self._btn_save.clicked.connect(self._on_save_json)
        btn_row.addWidget(self._btn_run)
        btn_row.addWidget(self._btn_reset)
        btn_row.addWidget(self._btn_load)
        btn_row.addWidget(self._btn_save)
        controls_lay.addLayout(btn_row)

        min_controls_h = (
            btn_add_type.sizeHint().height()
            + self._btn_run.minimumHeight()
            + 42
        )
        controls_section.setMinimumHeight(min_controls_h)

        self._item_split.addWidget(table_section)
        self._item_split.addWidget(controls_section)
        self._item_split.setStretchFactor(0, 1)
        self._item_split.setStretchFactor(1, 0)
        self._item_split.setCollapsible(0, False)
        self._item_split.setCollapsible(1, False)
        self._item_split.setSizes([280, min_controls_h])
        table_section.setMinimumHeight(self._table.minimumHeight())

        left_lay.addWidget(self._item_split, 1)

        # Center: canvas
        right = StyledFrame()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(20, 20, 20, 20)
        rl.setSpacing(16)
        cv_title = QLabel("Visualization")
        cv_title.setObjectName("cardTitle")
        rl.addWidget(cv_title)
        self._kpi_row = QGridLayout()
        self._kpi_row.setContentsMargins(0, 0, 0, 0)
        self._kpi_row.setHorizontalSpacing(10)
        self._kpi_row.setVerticalSpacing(10)
        self._kpi_cards: list[QWidget] = []
        self._kpi_util_value = self._create_kpi_card("Utilization", "—")
        self._kpi_placed_value = self._create_kpi_card("Placed / Unplaced", "—")
        self._kpi_time_value = self._create_kpi_card("Solve Time", "—")
        self._layout_kpi_cards()
        rl.addLayout(self._kpi_row)
        self._scene = PackingScene()
        self._view = PackingGraphicsView()
        self._view.setScene(self._scene)
        self._scene.box_clicked.connect(self._on_canvas_box_clicked)
        self._scene.box_hovered.connect(self._on_canvas_box_hovered)
        rl.addWidget(self._view, 1)

        split_h.addWidget(left)
        split_h.addWidget(right)
        split_h.setStretchFactor(0, 0)
        split_h.setStretchFactor(1, 1)

        self._log = LogPanel()
        self._log.clear_clicked.connect(lambda: _LOG.info("Logger cleared by user"))

        split_v.addWidget(split_h)
        split_v.addWidget(self._log)
        split_v.setStretchFactor(0, 1)
        split_v.setStretchFactor(1, 0)

        outer.addWidget(split_v, 1)

        self._log_emit = _LogEmitter()
        self._log_emit.line.connect(self._log.append_line)
        configure_logging(self._log_emit.line)
        self._table.selection_changed.connect(self._on_table_selection_changed)
        self._table.hover_changed.connect(self._on_table_hover_changed)

        self._on_inputs_changed()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._apply_item_split_constraints()
        self._layout_kpi_cards()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_item_split_constraints()
        self._layout_kpi_cards()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched in (self._spin_w, self._spin_h, self._spin_g) and event.type() == QEvent.Wheel:
            # Prevent accidental pallet value edits while scrolling.
            event.ignore()
            return True
        return super().eventFilter(watched, event)

    def _build_problem(self) -> PackingProblem:
        d = {
            "bin": {"W": self._spin_w.value(), "H": self._spin_h.value(), "g": self._spin_g.value()},
            "items": self._table.to_items_payload(),
        }
        return build_problem_from_dict(d)

    def _on_inputs_changed(self) -> None:
        try:
            p = self._build_problem()
            vr = validate(p)
        except Exception as e:
            self._btn_run.setEnabled(False)
            self._set_status_state("INVALID")
            self._set_kpis("—", "—", "—")
            return
        self._btn_run.setEnabled(vr.ok)
        if vr.ok:
            self._set_status_state("VALID")
        else:
            self._set_status_state("INVALID")

    def _on_run(self) -> None:
        if self._solve_thread and self._solve_thread.isRunning():
            return
        try:
            problem = self._build_problem()
        except Exception as e:
            QMessageBox.warning(self, "Input error", str(e))
            return
        vr = validate(problem)
        if not vr.ok:
            QMessageBox.warning(self, "Validation", "\n".join(vr.errors))
            return
        self._btn_run.setEnabled(False)
        _LOG.info("Solve started.")
        self._solve_thread = SolveThread(problem)
        self._solve_thread.finished_ok.connect(self._on_solve_ok)
        self._solve_thread.finished_error.connect(self._on_solve_err)
        self._solve_thread.finished.connect(self._on_solve_finished)
        self._solve_thread.start()

    def _on_solve_finished(self) -> None:
        self._btn_run.setEnabled(True)
        self._on_inputs_changed()

    def _on_solve_ok(self, sol: object) -> None:
        assert isinstance(sol, PackingSolution)
        self._last_solution = sol
        bs = sol.bin_spec
        self._scene.draw_solution(bs, sol)
        self._view.fit_bin(bs.width, bs.height)
        placed = sol.placed_count
        unplaced = sum(sol.unplaced_by_type.values())
        util = sol.utilization * 100.0
        _LOG.info(
            "Solve finished: placed=%s unplaced=%s util=%.2f%% time=%.4fs",
            placed,
            unplaced,
            util,
            sol.solve_time_s,
        )
        if unplaced:
            _LOG.warning("Partial solution: unplaced by type %s", sol.unplaced_by_type)
        unplaced_txt = str(sol.unplaced_by_type) if sol.unplaced_by_type else "{}"
        self._set_status_state("PARTIAL" if unplaced else "VALID")
        self._last_run_label.setText(f"Last run: {datetime.now().strftime('%H:%M:%S')}")
        self._set_kpis(
            f"{util:.2f}%",
            f"{placed} / {unplaced}",
            f"{sol.solve_time_s:.4f}s",
        )
        if unplaced_txt != "{}":
            _LOG.info("Unplaced detail: %s", unplaced_txt)

    def _on_solve_err(self, msg: str) -> None:
        _LOG.error("Solve error:\n%s", msg)
        QMessageBox.critical(self, "Solve error", msg[:2000])

    def _on_reset_scene(self) -> None:
        self._last_solution = None
        try:
            p = self._build_problem()
            bs = p.bin_spec
            self._scene.draw_solution(bs, None)
            self._view.fit_bin(bs.width, bs.height)
        except Exception:
            self._scene.clear_scene()
        _LOG.info("Scene reset.")
        self._set_kpis("—", "—", "—")
        self._set_status_state("INVALID")

    def _on_load_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load problem JSON", "", "JSON (*.json)")
        if not path:
            return
        try:
            prob = load_problem_from_json_file(path)
            vr = validate(prob)
            self._scenario_name = Path(path).name
            self._scenario_label.setText(f"Scenario: {self._scenario_name}")
            b = prob.bin_spec
            self._spin_w.setValue(b.width)
            self._spin_h.setValue(b.height)
            self._spin_g.setValue(b.gap)
            payload = [
                {
                    "w": it.width,
                    "h": it.height,
                    "q": it.quantity,
                    "rotation": it.allow_rotation,
                }
                for it in prob.item_types
            ]
            self._table.load_items(payload)
            if not vr.ok:
                _LOG.warning("Loaded JSON failed validation: %s", vr.errors)
            else:
                _LOG.info("Loaded JSON: %s", path)
            self._on_reset_scene()
        except Exception as e:
            _LOG.error("Load failed: %s", e)
            QMessageBox.warning(self, "Load error", str(e))

    def _on_save_json(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save problem JSON", "", "JSON (*.json)")
        if not path:
            return
        p = Path(path)
        try:
            prob = self._build_problem()
            save_problem_to_json_file(prob, p)
            _LOG.info("Saved JSON: %s", p)
        except Exception as e:
            _LOG.error("Save failed: %s", e)
            QMessageBox.warning(self, "Save error", str(e))

    def _apply_item_split_constraints(self) -> None:
        if not hasattr(self, "_item_split"):
            return
        split_max = max(260, self.height() - self._LEFT_NON_SPLITTER_RESERVED_HEIGHT)
        self._item_split.setMaximumHeight(split_max)

    def _create_kpi_card(self, title: str, value: str) -> QLabel:
        card = QWidget()
        card.setObjectName("kpiCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)
        ttl = QLabel(title)
        ttl.setObjectName("kpiTitle")
        val = QLabel(value)
        val.setObjectName("kpiValue")
        lay.addWidget(ttl)
        lay.addWidget(val)
        self._kpi_cards.append(card)
        return val

    def _layout_kpi_cards(self) -> None:
        if not hasattr(self, "_kpi_row"):
            return
        width = self.width()
        if width < 900:
            cols = 1
        elif width < 1280:
            cols = 2
        else:
            cols = 3
        while self._kpi_row.count():
            self._kpi_row.takeAt(0)
        for idx, card in enumerate(self._kpi_cards):
            row = idx // cols
            col = idx % cols
            self._kpi_row.addWidget(card, row, col)
        for col in range(cols):
            self._kpi_row.setColumnStretch(col, 1)

    def _set_kpis(self, util: str, placed: str, solve_time: str) -> None:
        self._kpi_util_value.setText(util)
        self._kpi_placed_value.setText(placed)
        self._kpi_time_value.setText(solve_time)

    def _set_status_state(self, state: str) -> None:
        state = state.upper()
        if state == "VALID":
            self._state_badge.setObjectName("statusBadgeValid")
        elif state == "PARTIAL":
            self._state_badge.setObjectName("statusBadgePartial")
        else:
            self._state_badge.setObjectName("statusBadgeInvalid")
            state = "INVALID"
        self._state_badge.setText(state)
        self._state_badge.style().unpolish(self._state_badge)
        self._state_badge.style().polish(self._state_badge)

    def _on_table_selection_changed(self, type_id: int) -> None:
        self._scene.highlight_type(type_id, mode="selected")

    def _on_table_hover_changed(self, type_id: int) -> None:
        self._scene.highlight_type(type_id, mode="hover")

    def _on_canvas_box_clicked(self, type_id: int) -> None:
        self._table.select_type_id(type_id)
        self._scene.highlight_type(type_id, mode="selected")

    def _on_canvas_box_hovered(self, _type_id: int) -> None:
        # Hover highlight is handled directly in scene; signal kept for table sync extension.
        return
