import pytest

from src.domain.bin_spec import BinSpec
from src.domain.item_type import ItemType
from src.domain.problem import PackingProblem
from src.validation.input_model import build_problem_from_dict
from src.validation.validate import validate


def test_validate_ok() -> None:
    p = PackingProblem(
        BinSpec(1000, 800, 5),
        (ItemType(0, 100, 50, 3, True),),
    )
    r = validate(p)
    assert r.ok
    assert not r.errors


def test_validate_negative_bin() -> None:
    p = PackingProblem(BinSpec(-1, 100, 0), ())
    r = validate(p)
    assert not r.ok


def test_validate_item_too_large_no_rotation() -> None:
    p = PackingProblem(
        BinSpec(100, 100, 0),
        (ItemType(1, 200, 10, 1, False),),
    )
    r = validate(p)
    assert not r.ok


def test_validate_rotation_allows_fit() -> None:
    p = PackingProblem(
        BinSpec(100, 100, 0),
        (ItemType(1, 80, 90, 1, True),),
    )
    r = validate(p)
    assert r.ok


def test_build_from_dict() -> None:
    d = {
        "bin": {"W": 1200, "H": 800, "g": 2},
        "items": [{"id": 0, "w": 100, "h": 50, "q": 2, "rotation": True}],
    }
    prob = build_problem_from_dict(d)
    assert prob.bin_spec.width == 1200
    assert len(prob.item_types) == 1
