from __future__ import annotations

from dataclasses import replace
import time

from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.solver.common.ordering import job_orderings_for_search
from src.solver.registry import DEFAULT_SOLVER_ID, create_solver


def _lex_better(a: PackingSolution, b: PackingSolution) -> bool:
    if a.placed_count != b.placed_count:
        return a.placed_count > b.placed_count
    return a.unused_area < b.unused_area


def solve(problem: PackingProblem, solver_id: str = DEFAULT_SOLVER_ID) -> PackingSolution:
    """
    Dispatches to selected solver.
    For plain maxrects, evaluates several deterministic piece orderings and returns
    lexicographically best layout (max placed, then min unused area).
    """
    t0 = time.perf_counter()
    solver = create_solver(solver_id)
    best: PackingSolution | None = None
    if solver_id == "maxrects":
        for jobs in job_orderings_for_search(problem.item_types):
            sol = solver.solve(problem, jobs)
            if best is None or _lex_better(sol, best):
                best = sol
        assert best is not None
    else:
        best = solver.solve(problem)
    t1 = time.perf_counter()
    return replace(best, solve_time_s=t1 - t0)
