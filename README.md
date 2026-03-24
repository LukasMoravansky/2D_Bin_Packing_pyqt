# 2D Single-Bin Packing (PyQt5)

Desktop application for **2D single-bin / pallet packing** with a modular **GUI** (`App/`) and **algorithmic core** (`src/`). Targets industrial-style benchmarks: validation, logging, reproducible setup, and tests.

![GUI screenshot](images/gui_screenshot.png)

*(Replace `images/gui_screenshot.png` with a capture of your running application.)*

## Problem

- One bin (pallet) of size **W × H** (mm).
- Item types **i**: footprint **wᵢ × hᵢ**, quantity **qᵢ**, optional **90° rotation**.
- **Minimum gap g** between any two placed items (no required gap to the bin border).
- **No overlap** between items; all items must lie inside the bin.
- **Optimization (lexicographic)**:
  1. Maximize the number of placed pieces.
  2. Among ties, minimize unused area \(W \cdot H - \sum \text{placed area}\).

If not everything fits, the solver returns a **valid partial** layout and **unplaced counts** per type.

## Requirements

- **Python** 3.10+
- **PyQt5** (GUI)
- **pytest** (tests, optional for end users)

## Installation

### Option A: pip (quick)

```bash
conda activate 2d-bin-packing
pip install -r requirements.txt
```

### Option B: Conda (scripts from benchmark spec)

- **Windows**: run `install.bat` (creates env `2d-bin-packing`, installs dependencies).
- **Linux/macOS**: `chmod +x install.sh && ./install.sh`

Then activate the environment and verify:

```bash
python verify.py
```

## Run

From the repository root (so `App` and `src` resolve on `sys.path`):

```bash
python -m App.main
```

## Project layout

| Path | Role |
|------|------|
| `App/` | PyQt5 entry point, main window, widgets, `QGraphicsView` / scene, worker thread |
| `src/` | Domain models, geometry (gap / overlap), validation, solver, JSON I/O — **no Qt** |
| `Data/` | Sample JSON instances (`sample_instances/`) |
| `Example/` | Headless batch solve (`run_batch.py`) |
| `Tests/` | Unit tests for geometry, validation, solver, smoke import |
| `images/` | README screenshot assets |

## Algorithms

- **Heuristic:** bottom-left placement on **maximal free rectangles** (maxrects): free space is tracked as disjoint axis-aligned rectangles; each piece is placed at the bottom-left corner of a free rectangle that fits, then that footprint is subtracted from all free regions. **Several deterministic piece orderings** are evaluated (max side / area / perimeter / aspect variants); the result **lexicographically maximizes** placed count, then minimizes unused bin area, matching the benchmark objective.
- **Legacy:** `SkylineSolver` remains in `src/solver/skyline.py` for comparison; the app uses `solve()` from `src/solver/interface.py`.
- **Gap handling:** Euclidean **minimum distance** between item footprints must be ≥ **g**; for **g = 0**, edge/corner contact is allowed but **positive-area overlap** is forbidden.
- The implementation is **deterministic** (no randomness) for benchmark traceability.

**Limits:** Maxrects is still a heuristic; it does not guarantee a global optimum for the lexicographic objective.

## JSON configuration

Files follow `schema_version: 1`.

```json
{
  "schema_version": 1,
  "bin": {
    "W": 1200,
    "H": 800,
    "g": 5
  },
  "items": [
    { "id": 0, "w": 300, "h": 200, "q": 3, "rotation": true }
  ]
}
```

- **W**, **H**: bin dimensions (mm).  
- **g**: minimum distance between items (mm).  
- **items**: each row has **w**, **h**, **q** (quantity), **rotation** (allow 90° swap), **id** (type id, optional; defaults to row index).

Load/save from the GUI via **Load JSON…** / **Save JSON…**.

## Tests

```bash
python -m pytest Tests
```

## Architecture notes

- **Separation:** `PackingProblem` / `PackingSolution` DTOs cross the GUI boundary; the worker runs `solve()` off the UI thread.
- **Logging:** Python `logging` with a Qt-safe bridge to the **System log** panel.
- **Visualization:** `QGraphicsScene` / `QGraphicsView` with technical-drawing style outlines and optional in-box dimension labels for large pieces.

## License

See `LICENSE` in the repository.
