from __future__ import annotations

from typing import Any

from src.domain.bin_spec import BinSpec
from src.domain.item_type import ItemType
from src.domain.problem import PackingProblem


def build_problem_from_dict(data: dict[str, Any]) -> PackingProblem:
    """Build PackingProblem from a canonical dict (GUI or JSON). Raises ValueError on bad shape."""
    # Ignore optional keys like schema_version
    bin_spec = data.get("bin") or data.get("pallet")
    if not isinstance(bin_spec, dict):
        raise ValueError("Missing 'bin' object")
    w = float(bin_spec["W"])
    h = float(bin_spec["H"])
    g = float(bin_spec["g"])
    items_raw = data.get("items")
    if not isinstance(items_raw, list):
        raise ValueError("Missing 'items' list")
    item_types: list[ItemType] = []
    for i, row in enumerate(items_raw):
        if not isinstance(row, dict):
            raise ValueError(f"items[{i}] must be an object")
        tid = int(row.get("id", i))
        wi = float(row["w"])
        hi = float(row["h"])
        qi = int(row["q"])
        rot = bool(row.get("rotation", row.get("allow_rotation", False)))
        item_types.append(ItemType(tid, wi, hi, qi, rot))
    return PackingProblem(BinSpec(w, h, g), tuple(item_types))
