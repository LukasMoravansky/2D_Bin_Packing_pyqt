from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlacedPiece:
    """One placed instance: position (bottom-left), footprint as placed, orientation flag."""

    type_id: int
    instance_index: int
    x: float
    y: float
    width: float
    height: float
    rotated: bool
