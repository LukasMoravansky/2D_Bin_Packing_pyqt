from __future__ import annotations

from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.solver.skyline import SkylineSolver


def solve(problem: PackingProblem) -> PackingSolution:
    """Deterministic skyline bottom-left heuristic."""
    return SkylineSolver().solve(problem)
