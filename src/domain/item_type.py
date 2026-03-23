from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ItemType:
    """One item species: footprint, quantity, optional 90° rotation."""

    type_id: int
    width: float
    height: float
    quantity: int
    allow_rotation: bool
