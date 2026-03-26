from __future__ import annotations

import traceback

from PyQt5.QtCore import QThread, pyqtSignal

from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.solver.registry import DEFAULT_SOLVER_ID
from src.solver.interface import solve
from src.validation.validate import validate


class SolveThread(QThread):
    """Runs packing solver off the GUI thread."""

    finished_ok = pyqtSignal(object)
    finished_error = pyqtSignal(str)

    def __init__(self, problem: PackingProblem, solver_id: str = DEFAULT_SOLVER_ID, parent=None) -> None:
        super().__init__(parent)
        self._problem = problem
        self._solver_id = solver_id

    def run(self) -> None:
        try:
            vr = validate(self._problem)
            if not vr.ok:
                self.finished_error.emit("Validation failed: " + "; ".join(vr.errors))
                return
            sol: PackingSolution = solve(self._problem, solver_id=self._solver_id)
            self.finished_ok.emit(sol)
        except Exception:
            self.finished_error.emit(traceback.format_exc())
