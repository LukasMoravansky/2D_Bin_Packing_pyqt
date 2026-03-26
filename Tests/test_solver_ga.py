from __future__ import annotations

from src.domain.bin_spec import BinSpec
from src.domain.item_type import ItemType
from src.domain.problem import PackingProblem
from src.geometry.gap import pairwise_gap_ok, rects_inside_bin
from src.geometry.rect import Rect
from src.solver.ga_solver import GAMaxRectsSolver
from src.solver.ga_solver.solver import GAConfig, _fitness_better, _fitness_tuple
from src.solver.interface import solve
from src.solver.registry import DEFAULT_SOLVER_ID, create_solver, list_solver_ids


def _demo_problem() -> PackingProblem:
    return PackingProblem(
        BinSpec(120, 80, 2),
        (
            ItemType(0, 35, 20, 4, True),
            ItemType(1, 30, 15, 5, True),
            ItemType(2, 50, 20, 2, False),
        ),
    )


def test_registry_contains_ga_maxrects() -> None:
    assert "ga_maxrects" in list_solver_ids()
    assert isinstance(create_solver("ga_maxrects"), GAMaxRectsSolver)


def test_default_solver_is_ga_maxrects() -> None:
    assert DEFAULT_SOLVER_ID == "ga_maxrects"


def test_ga_solution_valid_and_lex_helpers() -> None:
    sol = solve(_demo_problem(), solver_id="ga_maxrects")
    rects = [Rect(p.x, p.y, p.width, p.height) for p in sol.placed]
    assert rects_inside_bin(rects, sol.bin_spec.width, sol.bin_spec.height)
    assert pairwise_gap_ok(rects, sol.bin_spec.gap)

    fit = _fitness_tuple(sol)
    assert fit == (sol.placed_count, -sol.unused_area)
    assert _fitness_better((5, -90.0), (5, -100.0))
    assert _fitness_better((6, -400.0), (5, -1.0))
    assert not _fitness_better((4, -10.0), (5, -999.0))


def test_ga_reproducible_with_fixed_seed() -> None:
    p = _demo_problem()
    cfg = GAConfig(seed=123, max_generations=30, max_time_s=0.6, population_size=20)
    s1 = GAMaxRectsSolver(cfg).solve(p)
    s2 = GAMaxRectsSolver(cfg).solve(p)
    assert s1.placed_count == s2.placed_count
    assert s1.unplaced_by_type == s2.unplaced_by_type
    assert tuple((x.x, x.y, x.width, x.height, x.type_id, x.instance_index, x.rotated) for x in s1.placed) == tuple(
        (x.x, x.y, x.width, x.height, x.type_id, x.instance_index, x.rotated) for x in s2.placed
    )


def test_ga_fallback_on_internal_failure(monkeypatch) -> None:
    solver = GAMaxRectsSolver(GAConfig(seed=7, max_generations=10, max_time_s=0.2, population_size=10))
    p = _demo_problem()

    def _boom(_: PackingProblem):
        raise RuntimeError("simulated ga failure")

    monkeypatch.setattr(solver, "_run_ga", _boom)

    fallback_sol = solver.solve(p)
    baseline_maxrects_sol = solve(p, solver_id="maxrects")
    assert fallback_sol.placed_count == baseline_maxrects_sol.placed_count
    assert fallback_sol.unplaced_by_type == baseline_maxrects_sol.unplaced_by_type
