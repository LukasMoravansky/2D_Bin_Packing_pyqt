# 2D Single-Bin Packing (PyQt5)

Desktop application for **2D single-bin / pallet packing** with a modular **GUI** (`App/`) and **algorithmic core** (`src/`). Targets industrial-style benchmarks: validation, logging, reproducible setup, and tests.

**[→ Interactive case study presentation](https://lukasmoravansky.github.io/2D_Bin_Packing_pyqt/)** — the full story of building this with Cursor: workflow, challenges, results.

## Benchmark Context (Personal Note)

This repository was built as part of an internal R&D benchmark at [JIC](https://www.jic.cz/cz/), where we compare AI coding tools on the same practical software task.  
I implemented this version in **Cursor**.

The benchmark assignment and evaluation framework is documented in `docs/Benchmark AI nástrojů - Stručné zadání a hodnotící rámec .pdf`.

### Why this repository exists

- compare AI-assisted development workflows in a realistic industrial-style task
- improve my own skills in working with Cursor and large project context
- document what "vibe coding" looks like in practice for a PyQt desktop app

### AI workflow used in this implementation

- **Cursor plan/build workflow:** first-shot planning and initial build were done with Composer 2
- **Cursor tier:** Pro
- **Agent usage:** additional agent calls were mostly in Auto mode
- **Process assets:** visual feedback loops were done manually from GUI screenshots; annotated iterations are in `images/temp/`
- **Custom AI setup:** project-specific rules, skills, and a subagent were created in `.cursor/`
- **UI focus:** significant effort was spent on front-end polish in PyQt, including critique-driven iteration
- **Historical note:** `src/solver/skyline.py` came from the early one-shot build phase and is intentionally kept as a baseline/legacy solver

### Visual reference credit

For UI direction, agents/subagents used the following image as a **visual target** and iteratively tried to reduce the gap between the current PyQt GUI and the target style:

- [D-Module Construction Management Platform (Dribbble)](https://dribbble.com/shots/27204733-D-Module-Construction-Management-Platform)

Important context:

- agents did **not** have access to source HTML/CSS or implementation code for the referenced page
- they worked only from the image and from feedback on current GUI shortcomings at each iteration step
- changes were applied to a **PyQt desktop app**, which is generally a harder transfer path than reusing existing web page code directly

### Transparency note

Most of the code was intentionally AI-generated and then iteratively corrected/refined by me.  
That is not a side effect, but the core purpose of this benchmark: evaluate practical strengths and limits of AI-assisted development.

---

## Application Overview

![GUI screenshot](images/gui_screenshot.png)

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

- **Python** 3.10+ (recommended: 3.11)
- **pip** (for dependency installation)
- **OS:** Windows / Linux / macOS

> Note: project dependencies are pinned in `requirements.txt`.
> `pytest` is only required when running the test suite.

## Installation

Choose **one** setup path below.

### Option A: venv + pip (cross-platform)

1. Create and activate virtual environment:

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Linux/macOS (bash/zsh):**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Option B: Conda via benchmark scripts

These scripts create environment `2d-bin-packing` and install dependencies.

- **Windows:** run:

```bat
install.bat
conda activate 2d-bin-packing
```

- **Linux/macOS:** run:

```bash
chmod +x install.sh
./install.sh
conda activate 2d-bin-packing
```

### Verify environment

```bash
python verify.py
```

## Run

From the repository root (important, so `App` and `src` resolve correctly):

```bash
python -m App.main
```

## Run tests

```bash
python -m pytest Tests
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

- **Default solver (`ga_maxrects`):** a deterministic **genetic algorithm (GA)** in `src/solver/ga_solver/solver.py` evolves piece order permutations and decodes each individual via the existing **MaxRects** placement engine. Objective is benchmark-aligned and strictly lexicographic: maximize placed count first, then minimize unused area.
- **Decoder / baseline (`maxrects`):** bottom-left placement on **maximal free rectangles**. Free space is tracked as disjoint axis-aligned rectangles; each placed footprint is subtracted from free regions. Multiple deterministic orderings are still available and used as seeds/fallback.
- **Legacy (`skyline`):** `SkylineSolver` remains available for comparison.
- **Determinism:** GA uses a seedable RNG (`random.Random(seed)`, default seed `42`). Same input + same seed yields the same output layout.
- **Robustness:** GA is a metaheuristic layer only. On any internal GA failure, solver automatically falls back to deterministic MaxRects and still returns a valid (possibly partial) solution.
- **Gap handling:** Euclidean **minimum distance** between item footprints must be ≥ **g**; for **g = 0**, edge/corner contact is allowed but **positive-area overlap** is forbidden.

**Trade-off:** GA usually finds denser layouts than single-order heuristics under the same time budget, but does not guarantee a global optimum.

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

## Solution export (JSON log)

After a successful run, you can export the computed solution from the **Visualization** panel using **Export Solution (JSON)…**.

- The button is enabled only when a fresh solution exists.
- If inputs change after a run, export is disabled until the solver is run again.
- Export is also disabled while the solver is running.

The exported file follows `schema_version: 1` and includes:

- placed piece coordinates (`x`, `y`)
- piece orientation (`rotated`)
- placed and unplaced counts
- solve time
- area utilization percentage

Example:

```json
{
  "schema_version": 1,
  "kind": "solution",
  "meta": {
    "exported_at_utc": "2026-03-26T09:45:12.345678+00:00",
    "solver_id": "ga_maxrects",
    "scenario_name": "sample_01.json"
  },
  "bin": {
    "W": 1200.0,
    "H": 800.0,
    "g": 5.0
  },
  "summary": {
    "placed_count": 12,
    "unplaced_count": 1,
    "unplaced_by_type": {
      "3": 1
    },
    "solve_time_s": 0.1423,
    "utilization_pct": 87.54,
    "used_area": 840000.0,
    "unused_area": 120000.0
  },
  "placed": [
    {
      "type_id": 0,
      "instance_index": 0,
      "x": 0.0,
      "y": 0.0,
      "width": 300.0,
      "height": 200.0,
      "rotated": false
    }
  ]
}
```

## Architecture notes

- **Separation:** `PackingProblem` / `PackingSolution` DTOs cross the GUI boundary; the worker runs `solve()` off the UI thread.
- **Logging:** Python `logging` with a Qt-safe bridge to the **System log** panel.
- **Visualization:** `QGraphicsScene` / `QGraphicsView` with technical-drawing style outlines and optional in-box dimension labels for large pieces.

## Solver interface contract

This section defines the required interface between any solver implementation and the rest of the project.

### Input and output types (mandatory)

- **Input:** `PackingProblem` (`src/domain/problem.py`)
  - `problem.bin_spec.width` (float): bin width
  - `problem.bin_spec.height` (float): bin height
  - `problem.bin_spec.gap` (float): minimum Euclidean distance between piece footprints
  - `problem.item_types` (tuple of `ItemType`)
- **Output:** `PackingSolution` (`src/domain/solution.py`)
  - `bin_spec`: copy/reference of the input bin spec
  - `placed`: tuple of `PlacedPiece` with final placement `(x, y, width, height, rotated)`
  - `unplaced_by_type`: `dict[int, int]` counting pieces that were not placed
  - `solve_time_s`: elapsed solve time in seconds (the dispatcher may overwrite this with end-to-end timing)

### Behavioral requirements (mandatory)

Every solver must return a **valid** solution:

- all placed rectangles are inside bin bounds
- no positive-area overlap is allowed
- pairwise minimum distance is at least `gap` (for `gap = 0`, edge/corner touch is allowed)
- partial solutions are allowed; unplaced pieces must be reported in `unplaced_by_type`

Validation is performed before solve in the worker (`src/validation/validate.py`), but solver output must still satisfy geometry rules.

### Dispatch and registration

- Solver selection is ID-based and centralized in `src/solver/registry.py`
- Add your solver factory/class to `_SOLVER_FACTORIES`
- The GUI solver dropdown is populated automatically from `list_solver_ids()`
- Solve dispatch goes through `src/solver/interface.py`

Current solver IDs:

- `ga_maxrects` (default)
- `maxrects`
- `skyline`

### Signature conventions

The project currently uses two solver call patterns:

- most solvers implement `solve(problem: PackingProblem) -> PackingSolution`
- `maxrects` is a special case that receives explicit job ordering through dispatcher internals

For new external/custom solvers, implement the standard form:

`solve(problem: PackingProblem) -> PackingSolution`

