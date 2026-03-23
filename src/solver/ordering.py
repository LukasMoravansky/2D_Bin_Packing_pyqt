from __future__ import annotations

from dataclasses import dataclass

from src.domain.item_type import ItemType


@dataclass(frozen=True, slots=True)
class PieceJob:
    """One unit to place (identity for unplaced accounting)."""

    type_id: int
    copy_index: int
    base_w: float
    base_h: float
    allow_rotation: bool


def expand_jobs(item_types: tuple[ItemType, ...]) -> list[PieceJob]:
    jobs: list[PieceJob] = []
    for it in item_types:
        for k in range(it.quantity):
            jobs.append(
                PieceJob(
                    type_id=it.type_id,
                    copy_index=k,
                    base_w=it.width,
                    base_h=it.height,
                    allow_rotation=it.allow_rotation,
                )
            )
    jobs.sort(
        key=lambda j: (
            -max(j.base_w, j.base_h),
            -(j.base_w * j.base_h),
            j.type_id,
            j.copy_index,
        )
    )
    return jobs
