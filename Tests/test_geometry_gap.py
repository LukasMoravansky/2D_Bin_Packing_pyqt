from math import sqrt

import pytest

from src.geometry.gap import min_distance, pairwise_gap_ok, rects_inside_bin
from src.geometry.rect import Rect


def test_min_distance_overlap() -> None:
    a = Rect(0, 0, 10, 10)
    b = Rect(5, 5, 10, 10)
    assert min_distance(a, b) == 0.0


def test_min_distance_touching_edge() -> None:
    a = Rect(0, 0, 10, 10)
    b = Rect(10, 0, 5, 5)
    assert min_distance(a, b) == 0.0


def test_min_distance_separated_horizontal() -> None:
    a = Rect(0, 0, 10, 10)
    b = Rect(12, 0, 5, 5)
    assert min_distance(a, b) == 2.0


def test_min_distance_separated_vertical() -> None:
    a = Rect(0, 0, 10, 10)
    b = Rect(0, 12, 5, 5)
    assert min_distance(a, b) == 2.0


def test_min_distance_diagonal_corner_gap() -> None:
    a = Rect(0, 0, 10, 10)
    b = Rect(13, 14, 5, 5)
    assert min_distance(a, b) == pytest.approx(sqrt(3 * 3 + 4 * 4))


def test_pairwise_gap_ok() -> None:
    r1 = Rect(0, 0, 10, 10)
    r2 = Rect(12, 0, 10, 10)
    assert pairwise_gap_ok([r1, r2], 2.0)
    assert not pairwise_gap_ok([r1, r2], 2.01)


def test_rects_inside_bin() -> None:
    assert rects_inside_bin([Rect(0, 0, 10, 10)], 100, 100)
    assert not rects_inside_bin([Rect(-1, 0, 10, 10)], 100, 100)
