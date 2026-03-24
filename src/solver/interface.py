from __future__ import annotations

from dataclasses import replace
import time

from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.solver.maxrects import MaxRectsSolver
from src.solver.ordering import job_orderings_for_search


def _lex_better(a: PackingSolution, b: PackingSolution) -> bool:
    if a.placed_count != b.placed_count:
        return a.placed_count > b.placed_count
    return a.unused_area < b.unused_area


def solve(problem: PackingProblem) -> PackingSolution:
    """
    Maximal free-rectangles (maxrects) bottom-left placement with several deterministic
    piece orderings; returns the lexicographically best layout (max placed, then min unused area).
    """
    t0 = time.perf_counter()
    solver = MaxRectsSolver()
    best: PackingSolution | None = None
    for jobs in job_orderings_for_search(problem.item_types):
        sol = solver.solve(problem, jobs)
        if best is None or _lex_better(sol, best):
            best = sol
    assert best is not None
    t1 = time.perf_counter()
    return replace(best, solve_time_s=t1 - t0)
