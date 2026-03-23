from __future__ import annotations

import time
from typing import Iterable

from src.domain.placed_piece import PlacedPiece
from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.geometry.gap import placement_valid
from src.geometry.rect import Rect
from src.solver.ordering import PieceJob, expand_jobs


def _merge_segments(segments: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    if not segments:
        return []
    segments = sorted(segments, key=lambda s: s[0])
    out: list[tuple[float, float, float]] = []
    cur_l, cur_r, cur_y = segments[0]
    for xl, xr, y in segments[1:]:
        if xl == cur_r and y == cur_y:
            cur_r = xr
        else:
            out.append((cur_l, cur_r, cur_y))
            cur_l, cur_r, cur_y = xl, xr, y
    out.append((cur_l, cur_r, cur_y))
    return out


def _cut_segment(
    xl: float, xr: float, y: float, px: float, pw: float, new_top: float
) -> list[tuple[float, float, float]]:
    """Replace height with new_top on overlap with [px, px+pw)."""
    px2 = px + pw
    parts: list[tuple[float, float, float]] = []
    if xr <= px or xl >= px2:
        return [(xl, xr, y)]
    if xl < px:
        parts.append((xl, min(xr, px), y))
    mid_l = max(xl, px)
    mid_r = min(xr, px2)
    if mid_l < mid_r:
        parts.append((mid_l, mid_r, new_top))
    if xr > px2:
        parts.append((max(xl, px2), xr, y))
    return parts


def _max_y_on_interval(
    segments: Iterable[tuple[float, float, float]], x0: float, x1: float
) -> float:
    m = 0.0
    for xl, xr, y in segments:
        lo = max(x0, xl)
        hi = min(x1, xr)
        if lo < hi:
            m = max(m, y)
    return m


def _candidate_x_positions(segments: list[tuple[float, float, float]], w: float, bin_w: float) -> list[float]:
    xs: set[float] = {0.0}
    for xl, xr, _ in segments:
        if xl + w <= bin_w + 1e-12:
            xs.add(xl)
        if xr - w >= -1e-12 and xr - w + w <= bin_w + 1e-12:
            xs.add(max(0.0, xr - w))
    return sorted(x for x in xs if x + w <= bin_w + 1e-12)


def _orientations(job: PieceJob) -> list[tuple[float, float, bool]]:
    w, h = job.base_w, job.base_h
    if job.allow_rotation:
        if abs(w - h) < 1e-15:
            return [(w, h, False)]
        return [(w, h, False), (h, w, True)]
    return [(w, h, False)]


class SkylineSolver:
    def solve(self, problem: PackingProblem) -> PackingSolution:
        t0 = time.perf_counter()
        b = problem.bin_spec
        gap = b.gap
        jobs = expand_jobs(problem.item_types)
        unplaced: dict[int, int] = {}

        segments: list[tuple[float, float, float]] = [(0.0, b.width, 0.0)]
        placed_rects: list[Rect] = []
        placed_pieces: list[PlacedPiece] = []

        for job in jobs:
            best: tuple[float, float, float, float, bool] | None = None
            best_key: tuple[float, float, float] | None = None

            for rw, rh, rot in _orientations(job):
                if rw > b.width + 1e-12 or rh > b.height + 1e-12:
                    continue
                xs = _candidate_x_positions(segments, rw, b.width)
                for x in xs:
                    y = _max_y_on_interval(segments, x, x + rw)
                    if y + rh > b.height + 1e-12:
                        continue
                    r = Rect(x, y, rw, rh)
                    if not placement_valid(r, placed_rects, gap):
                        continue
                    # Minimize y, then x, then maximize top (tighter packing proxy)
                    key = (y, x, -(y + rh))
                    if best_key is None or key < best_key:
                        best = (x, y, rw, rh, rot)
                        best_key = key

            if best is None:
                unplaced[job.type_id] = unplaced.get(job.type_id, 0) + 1
                continue

            x, y, rw, rh, rot = best
            new_top = y + rh
            new_segs: list[tuple[float, float, float]] = []
            for xl, xr, y0 in segments:
                new_segs.extend(_cut_segment(xl, xr, y0, x, rw, new_top))
            segments = _merge_segments(new_segs)
            r = Rect(x, y, rw, rh)
            placed_rects.append(r)
            placed_pieces.append(
                PlacedPiece(
                    type_id=job.type_id,
                    instance_index=job.copy_index,
                    x=x,
                    y=y,
                    width=rw,
                    height=rh,
                    rotated=rot,
                )
            )

        t1 = time.perf_counter()
        return PackingSolution(
            bin_spec=problem.bin_spec,
            placed=tuple(placed_pieces),
            unplaced_by_type=unplaced,
            solve_time_s=t1 - t0,
        )
