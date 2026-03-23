from __future__ import annotations

from dataclasses import dataclass

from src.domain.bin_spec import BinSpec
from src.domain.placed_piece import PlacedPiece


@dataclass(frozen=True, slots=True)
class PackingSolution:
    """Solver output: placed pieces, unplaced counts, timing, utilization."""

    bin_spec: BinSpec
    placed: tuple[PlacedPiece, ...]
    unplaced_by_type: dict[int, int]
    solve_time_s: float

    @property
    def placed_count(self) -> int:
        return len(self.placed)

    @property
    def bin_area(self) -> float:
        b = self.bin_spec
        return b.width * b.height

    @property
    def used_area(self) -> float:
        return sum(p.width * p.height for p in self.placed)

    @property
    def unused_area(self) -> float:
        return self.bin_area - self.used_area

    @property
    def utilization(self) -> float:
        if self.bin_area <= 0:
            return 0.0
        return self.used_area / self.bin_area
