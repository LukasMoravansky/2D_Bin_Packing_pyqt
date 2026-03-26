from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.domain.problem import PackingProblem
from src.domain.solution import PackingSolution
from src.validation.input_model import build_problem_from_dict


SCHEMA_VERSION = 1


def problem_to_dict(problem: PackingProblem) -> dict[str, Any]:
    b = problem.bin_spec
    return {
        "schema_version": SCHEMA_VERSION,
        "bin": {"W": b.width, "H": b.height, "g": b.gap},
        "items": [
            {
                "id": it.type_id,
                "w": it.width,
                "h": it.height,
                "q": it.quantity,
                "rotation": it.allow_rotation,
            }
            for it in problem.item_types
        ],
    }


def dict_to_problem(data: dict[str, Any]) -> PackingProblem:
    sv = data.get("schema_version", 1)
    if int(sv) != SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema_version {sv!r}, expected {SCHEMA_VERSION}")
    return build_problem_from_dict(data)


def load_problem_from_json_file(path: str | Path) -> PackingProblem:
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return dict_to_problem(data)


def save_problem_to_json_file(problem: PackingProblem, path: str | Path) -> None:
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        json.dump(problem_to_dict(problem), f, indent=2)
        f.write("\n")


def solution_to_dict(
    solution: PackingSolution,
    *,
    solver_id: str | None = None,
    scenario_name: str | None = None,
) -> dict[str, Any]:
    b = solution.bin_spec
    unplaced_count = sum(solution.unplaced_by_type.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "solution",
        "meta": {
            "exported_at_utc": datetime.now(timezone.utc).isoformat(),
            "solver_id": solver_id,
            "scenario_name": scenario_name,
        },
        "bin": {"W": b.width, "H": b.height, "g": b.gap},
        "summary": {
            "placed_count": solution.placed_count,
            "unplaced_count": unplaced_count,
            "unplaced_by_type": solution.unplaced_by_type,
            "solve_time_s": solution.solve_time_s,
            "utilization_pct": solution.utilization * 100.0,
            "used_area": solution.used_area,
            "unused_area": solution.unused_area,
        },
        "placed": [
            {
                "type_id": p.type_id,
                "instance_index": p.instance_index,
                "x": p.x,
                "y": p.y,
                "width": p.width,
                "height": p.height,
                "rotated": p.rotated,
            }
            for p in solution.placed
        ],
    }


def save_solution_to_json_file(
    solution: PackingSolution,
    path: str | Path,
    *,
    solver_id: str | None = None,
    scenario_name: str | None = None,
) -> None:
    p = Path(path)
    data = solution_to_dict(solution, solver_id=solver_id, scenario_name=scenario_name)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
