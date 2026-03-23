from __future__ import annotations

from src.geometry.rect import Rect


def min_distance(a: Rect, b: Rect) -> float:
    """
    Minimum Euclidean distance between the two closed axis-aligned rectangles.
    Returns 0 if they overlap or touch (edge or corner).
    """
    ax1, ay1, ax2, ay2 = a.x, a.y, a.right, a.top
    bx1, by1, bx2, by2 = b.x, b.y, b.right, b.top

    # Horizontal gap (positive if separated horizontally)
    if ax2 < bx1:
        dx = bx1 - ax2
    elif bx2 < ax1:
        dx = ax1 - bx2
    else:
        dx = 0.0

    # Vertical gap
    if ay2 < by1:
        dy = by1 - ay2
    elif by2 < ay1:
        dy = ay1 - by2
    else:
        dy = 0.0

    if dx == 0.0 and dy == 0.0:
        return 0.0
    if dx == 0.0:
        return dy
    if dy == 0.0:
        return dx
    from math import sqrt

    return sqrt(dx * dx + dy * dy)


def pairwise_gap_ok(rects: list[Rect], gap: float) -> bool:
    """True if every pair has min_distance >= gap."""
    n = len(rects)
    for i in range(n):
        for j in range(i + 1, n):
            if min_distance(rects[i], rects[j]) + 1e-9 < gap:
                return False
    return True


def rect_inside_bin(r: Rect, bin_w: float, bin_h: float) -> bool:
    return r.x >= 0 and r.y >= 0 and r.right <= bin_w and r.top <= bin_h


def rects_inside_bin(rects: list[Rect], bin_w: float, bin_h: float) -> bool:
    return all(rect_inside_bin(r, bin_w, bin_h) for r in rects)


def positive_overlap(a: Rect, b: Rect) -> bool:
    """True if closed rectangles overlap with positive area (edge/corner touch is not overlap)."""
    ix = min(a.right, b.right) - max(a.x, b.x)
    iy = min(a.top, b.top) - max(a.y, b.y)
    return ix > 0 and iy > 0


def placement_valid(new: Rect, placed: list[Rect], gap: float) -> bool:
    """No positive overlap; if gap > 0, Euclidean distance between rects must be >= gap."""
    eps = 1e-9
    for p in placed:
        if gap > eps:
            if min_distance(new, p) + eps < gap:
                return False
        elif positive_overlap(new, p):
            return False
    return True
