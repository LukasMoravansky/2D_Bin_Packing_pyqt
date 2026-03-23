from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.problem import PackingProblem


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _fits_in_bin(w: float, h: float, bw: float, bh: float) -> bool:
    return (w <= bw and h <= bh) or (h <= bw and w <= bh)


def validate(problem: PackingProblem) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    b = problem.bin_spec
    if b.width <= 0 or b.height <= 0:
        errors.append("Bin width and height must be positive.")
    if b.gap < 0:
        errors.append("Gap g must be non-negative.")

    if not problem.item_types:
        warnings.append("No item types defined.")

    for it in problem.item_types:
        if it.quantity < 0:
            errors.append(f"Item type {it.type_id}: quantity must be non-negative.")
        if it.width <= 0 or it.height <= 0:
            errors.append(f"Item type {it.type_id}: width and height must be positive.")
        if it.quantity > 0:
            can_place = False
            if it.allow_rotation:
                can_place = _fits_in_bin(it.width, it.height, b.width, b.height)
            else:
                can_place = it.width <= b.width and it.height <= b.height
            if not can_place:
                errors.append(
                    f"Item type {it.type_id}: cannot fit inside bin in any allowed orientation."
                )

    return ValidationResult(ok=len(errors) == 0, errors=errors, warnings=warnings)
