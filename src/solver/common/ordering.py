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


def _collect_jobs(item_types: tuple[ItemType, ...]) -> list[PieceJob]:
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
    return jobs


def expand_jobs(item_types: tuple[ItemType, ...]) -> list[PieceJob]:
    """Default ordering: decreasing max side, then area (skyline / legacy)."""
    jobs = _collect_jobs(item_types)
    jobs.sort(
        key=lambda j: (
            -max(j.base_w, j.base_h),
            -(j.base_w * j.base_h),
            j.type_id,
            j.copy_index,
        )
    )
    return jobs


def job_orderings_for_search(item_types: tuple[ItemType, ...]) -> list[list[PieceJob]]:
    """
    Several deterministic piece sequences for multi-start packing.
    Lexicographic tie-break uses (type_id, copy_index) for stability.
    """
    base = _collect_jobs(item_types)
    if not base:
        return [[]]

    def key_max_side_area(j: PieceJob) -> tuple:
        return (-max(j.base_w, j.base_h), -(j.base_w * j.base_h), j.type_id, j.copy_index)

    def key_area_max_side(j: PieceJob) -> tuple:
        return (-(j.base_w * j.base_h), -max(j.base_w, j.base_h), j.type_id, j.copy_index)

    def key_perimeter_area(j: PieceJob) -> tuple:
        p = 2.0 * (j.base_w + j.base_h)
        return (-p, -(j.base_w * j.base_h), j.type_id, j.copy_index)

    def key_min_side_asc(j: PieceJob) -> tuple:
        return (min(j.base_w, j.base_h), j.type_id, j.copy_index)

    def key_max_side_asc_area(j: PieceJob) -> tuple:
        return (max(j.base_w, j.base_h), -(j.base_w * j.base_h), j.type_id, j.copy_index)

    def key_aspect_then_area(j: PieceJob) -> tuple:
        ar = j.base_w / j.base_h if j.base_h > 1e-15 else 0.0
        return (-abs(ar - 1.0), -(j.base_w * j.base_h), j.type_id, j.copy_index)

    strategies = (
        key_max_side_area,
        key_area_max_side,
        key_perimeter_area,
        key_min_side_asc,
        key_max_side_asc_area,
        key_aspect_then_area,
    )

    out: list[list[PieceJob]] = []
    seen: set[tuple[tuple[int, int], ...]] = set()
    for strat in strategies:
        jobs = list(base)
        jobs.sort(key=strat)
        sig = tuple((j.type_id, j.copy_index) for j in jobs)
        if sig in seen:
            continue
        seen.add(sig)
        out.append(jobs)
    return out
