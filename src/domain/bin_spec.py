from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BinSpec:
    """Pallet / single bin dimensions and minimum gap between placed items (mm)."""

    width: float
    height: float
    gap: float
