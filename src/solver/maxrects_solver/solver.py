from __future__ import annotations

import time
from typing import Iterable

from src.domain.placed_piece import PlacedPiece
from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.geometry.gap import placement_valid
from src.geometry.rect import Rect
from src.solver.common.ordering import PieceJob

_EPS = 1e-9


def _intersect_rect(a: Rect, b: Rect) -> Rect | None:
    x0 = max(a.x, b.x)
    y0 = max(a.y, b.y)
    x1 = min(a.right, b.right)
    y1 = min(a.top, b.top)
    w = x1 - x0
    h = y1 - y0
    if w <= _EPS or h <= _EPS:
        return None
    return Rect(x0, y0, w, h)


def _positive_overlap(a: Rect, b: Rect) -> bool:
    ix = min(a.right, b.right) - max(a.x, b.x)
    iy = min(a.top, b.top) - max(a.y, b.y)
    return ix > _EPS and iy > _EPS


def _subtract_solid(f: Rect, solid: Rect) -> list[Rect]:
    """Axis-aligned pieces of f not covered by solid (closed rects; shared edges OK)."""
    clip = _intersect_rect(f, solid)
    if clip is None:
        return [f]
    out: list[Rect] = []
    # Bottom strip
    if clip.y > f.y + _EPS:
        out.append(Rect(f.x, f.y, f.width, clip.y - f.y))
    # Top strip
    if f.top > clip.top + _EPS:
        out.append(Rect(f.x, clip.top, f.width, f.top - clip.top))
    # Middle band [clip.y, clip.top]
    mid_h = clip.height
    if mid_h > _EPS:
        if clip.x > f.x + _EPS:
            out.append(Rect(f.x, clip.y, clip.x - f.x, mid_h))
        if f.right > clip.right + _EPS:
            out.append(Rect(clip.right, clip.y, f.right - clip.right, mid_h))
    return [r for r in out if r.width > _EPS and r.height > _EPS]


def _contains(a: Rect, b: Rect) -> bool:
    return (
        a.x <= b.x + _EPS
        and a.y <= b.y + _EPS
        and a.right >= b.right - _EPS
        and a.top >= b.top - _EPS
    )


def _prune_free_rects(rects: list[Rect]) -> list[Rect]:
    rects = [r for r in rects if r.width > _EPS and r.height > _EPS]
    rects.sort(key=lambda r: r.width * r.height, reverse=True)
    kept: list[Rect] = []
    for r in rects:
        if any(_contains(k, r) for k in kept):
            continue
        kept.append(r)
    return kept


def _update_free_rects(free: list[Rect], solid: Rect) -> list[Rect]:
    nxt: list[Rect] = []
    for f in free:
        if _positive_overlap(f, solid):
            nxt.extend(_subtract_solid(f, solid))
        else:
            nxt.append(f)
    return _prune_free_rects(nxt)


def _orientations(job: PieceJob) -> list[tuple[float, float, bool]]:
    w, h = job.base_w, job.base_h
    if job.allow_rotation:
        if abs(w - h) < 1e-15:
            return [(w, h, False)]
        return [(w, h, False), (h, w, True)]
    return [(w, h, False)]


def _placement_key(y: float, x: float, rh: float) -> tuple[float, float, float]:
    return (y, x, -(y + rh))


def _axis_candidates(start: float, end: float, size: float, gap: float) -> list[float]:
    """
    Candidate coordinates inside [start, end-size].
    Includes edge anchors and gap-shifted anchors to avoid missing valid placements
    when inter-item clearance forces a small slide (e.g. +g).
    """
    hi = end - size
    if hi < start - _EPS:
        return []
    raw = [
        start,
        hi,
        start + gap,
        hi - gap,
    ]
    out: list[float] = []
    for v in raw:
        if v < start - _EPS or v > hi + _EPS:
            continue
        vv = start if abs(v - start) <= _EPS else hi if abs(v - hi) <= _EPS else v
        if any(abs(vv - u) <= _EPS for u in out):
            continue
        out.append(vv)
    out.sort()
    return out


class MaxRectsSolver:
    """
    Maximal free-rectangle heuristic: maintain free space as disjoint rects, place each
    piece bottom-left inside a free rect, subtract solid from all free rects.
    Candidates are validated with the same Euclidean-gap rules as the rest of the app.
    """

    def solve(self, problem: PackingProblem, jobs: Iterable[PieceJob]) -> PackingSolution:
        """
        Place jobs in order using bottom-left preference among valid candidates.

        The method maintains a list of maximal free rectangles and updates them
        after each accepted placement. All candidates are checked against gap
        and overlap constraints via shared geometry validation.
        """
        t0 = time.perf_counter()
        b = problem.bin_spec
        gap = b.gap
        job_list = list(jobs)
        unplaced: dict[int, int] = {}

        free: list[Rect] = [Rect(0.0, 0.0, b.width, b.height)]
        placed_rects: list[Rect] = []
        placed_pieces: list[PlacedPiece] = []

        for job in job_list:
            best: tuple[float, float, float, float, bool] | None = None
            best_key: tuple[float, float, float] | None = None

            for rw, rh, rot in _orientations(job):
                if rw > b.width + _EPS or rh > b.height + _EPS:
                    continue
                for fr in free:
                    if fr.width + _EPS < rw or fr.height + _EPS < rh:
                        continue
                    xs = _axis_candidates(fr.x, fr.right, rw, gap)
                    ys = _axis_candidates(fr.y, fr.top, rh, gap)
                    for x in xs:
                        for y in ys:
                            r = Rect(x, y, rw, rh)
                            if r.right > b.width + _EPS or r.top > b.height + _EPS:
                                continue
                            if not placement_valid(r, placed_rects, gap):
                                continue
                            key = _placement_key(y, x, rh)
                            if best_key is None or key < best_key:
                                best = (x, y, rw, rh, rot)
                                best_key = key

            if best is None:
                # Keep partial solutions valid and report unplaced pieces by type.
                unplaced[job.type_id] = unplaced.get(job.type_id, 0) + 1
                continue

            x, y, rw, rh, rot = best
            solid = Rect(x, y, rw, rh)
            placed_rects.append(solid)
            free = _update_free_rects(free, solid)
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
