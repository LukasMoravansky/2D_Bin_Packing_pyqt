from __future__ import annotations

from typing import Callable

from src.solver.ga_solver import GAMaxRectsSolver
from src.solver.maxrects_solver import MaxRectsSolver
from src.solver.skyline_solver import SkylineSolver


SolverFactory = Callable[[], object]

DEFAULT_SOLVER_ID = "ga_maxrects"

_SOLVER_FACTORIES: dict[str, SolverFactory] = {
    "ga_maxrects": GAMaxRectsSolver,
    "maxrects": MaxRectsSolver,
    "skyline": SkylineSolver,
}


def list_solver_ids() -> tuple[str, ...]:
    return tuple(_SOLVER_FACTORIES.keys())


def create_solver(solver_id: str = DEFAULT_SOLVER_ID) -> object:
    try:
        factory = _SOLVER_FACTORIES[solver_id]
    except KeyError as exc:
        available = ", ".join(list_solver_ids())
        raise ValueError(f"Unknown solver '{solver_id}'. Available: {available}") from exc
    return factory()
