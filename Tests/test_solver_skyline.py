from src.domain.bin_spec import BinSpec
from src.domain.item_type import ItemType
from src.domain.problem import PackingProblem
from src.geometry.gap import placement_valid, positive_overlap
from src.geometry.rect import Rect
from src.solver.interface import solve


def test_solve_single_item() -> None:
    p = PackingProblem(
        BinSpec(100, 100, 0),
        (ItemType(0, 30, 40, 1, False),),
    )
    sol = solve(p)
    assert sol.placed_count == 1
    assert sol.unplaced_by_type == {}
    assert sol.utilization > 0


def test_gap_separates_items() -> None:
    p = PackingProblem(
        BinSpec(100, 20, 5),
        (
            ItemType(0, 40, 10, 2, False),
        ),
    )
    sol = solve(p)
    assert sol.placed_count == 2
    r0 = Rect(sol.placed[0].x, sol.placed[0].y, sol.placed[0].width, sol.placed[0].height)
    r1 = Rect(sol.placed[1].x, sol.placed[1].y, sol.placed[1].width, sol.placed[1].height)
    assert not positive_overlap(r0, r1)


def test_placement_valid_gap_zero_touch() -> None:
    a = Rect(0, 0, 10, 10)
    b = Rect(10, 0, 5, 5)
    assert placement_valid(b, [a], 0.0)


def test_placement_valid_gap_zero_no_overlap() -> None:
    a = Rect(0, 0, 10, 10)
    b = Rect(5, 5, 5, 5)
    assert not placement_valid(b, [a], 0.0)


def test_partial_unplaced() -> None:
    p = PackingProblem(
        BinSpec(10, 10, 0),
        (
            ItemType(0, 9, 9, 1, False),
            ItemType(1, 9, 9, 1, False),
        ),
    )
    sol = solve(p)
    assert sol.placed_count == 1
    assert sum(sol.unplaced_by_type.values()) == 1
