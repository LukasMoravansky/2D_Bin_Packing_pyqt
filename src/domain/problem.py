from __future__ import annotations

from dataclasses import dataclass

from src.domain.bin_spec import BinSpec
from src.domain.item_type import ItemType


@dataclass(frozen=True, slots=True)
class PackingProblem:
    """Full input to the solver."""

    bin_spec: BinSpec
    item_types: tuple[ItemType, ...]
