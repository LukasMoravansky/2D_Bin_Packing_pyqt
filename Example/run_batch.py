"""Headless solve over JSON instances in Data/sample_instances/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io.json_config import load_problem_from_json_file
from src.solver.interface import solve
from src.validation.validate import validate


def main() -> None:
    sample_dir = ROOT / "Data" / "sample_instances"
    if not sample_dir.is_dir():
        print("No sample_instances directory")
        return
    for path in sorted(sample_dir.glob("*.json")):
        prob = load_problem_from_json_file(path)
        vr = validate(prob)
        if not vr.ok:
            print(path.name, "INVALID", vr.errors)
            continue
        sol = solve(prob)
        print(
            path.name,
            "placed",
            sol.placed_count,
            "unplaced",
            sol.unplaced_by_type,
            f"util={sol.utilization:.3f}",
            f"t={sol.solve_time_s:.4f}s",
        )


if __name__ == "__main__":
    main()
