---
name: pyqt-gui-front-end-design
description: Design and polish high-quality PyQt5 desktop interfaces for benchmark-style GUI applications. Use when the user asks for top-notch GUI/front-end design, visual refinement, styling, layout improvements, or UX polish in Python/PyQt projects.
---

# PyQt GUI Front-End Design

Use this skill to turn functional PyQt5 screens into production-grade desktop interfaces with strong visual hierarchy, consistent styling, and clear interaction flow.

## Scope

- Prioritize GUI/UX quality: layout, spacing, typography, color system, component states, and readability.
- Keep the workflow practical for benchmark/engineering tools.
- Avoid redesigning core algorithms, architecture, or data model unless explicitly requested.

## Design Workflow

1. Understand the screen's purpose and key user flow.
2. Choose one clear visual direction (for example: technical-minimal, industrial-clean, control-room high contrast).
3. Define a compact design system:
   - Typography scale for titles, labels, values, and helper text
   - Color roles: surface, text, accent, info, warning, error, success
   - Spacing rhythm and panel structure
4. Apply structure first, then polish:
   - Organize with `QHBoxLayout`, `QVBoxLayout`, `QGridLayout`
   - Group controls into clear sections
   - Improve alignment, margins, and spacing consistency
5. Style states deliberately:
   - `QPushButton`: default, hover, pressed, disabled
   - Inputs (`QLineEdit`, `QComboBox`, tables): focus, hover, invalid
   - Logging/output areas: semantic coloring for info/warn/error/success
6. Validate usability:
   - Text contrast remains readable
   - Inputs and actions are easy to scan
   - Visualization/logging areas remain legible under real use

## PyQt5 Implementation Rules

- Prefer centralized style constants (palette, spacing, radius, font sizes) over scattered values.
- Use Qt Style Sheets intentionally; avoid one-off overrides unless needed.
- Preserve predictable behavior and keyboard/mouse usability.
- Ensure placed/unplaced or success/error states are visually distinct in scenes and logs.
- Keep styling cohesive across all panels and widgets.

## Quality Bar

- No generic template look.
- No inconsistent spacing or random color use.
- No weak contrast in primary text or critical controls.
- No visual noise that reduces workflow clarity.

## Response Format

When executing a request with this skill:

1. State the chosen visual direction in one sentence.
2. List the design-system decisions (typography, color roles, spacing).
3. Implement concrete PyQt5 code updates.
4. End with a short verification checklist:
   - layout hierarchy is clear
   - widget states are styled
   - logger/feedback semantics are visible
   - main workflow remains fast to use
