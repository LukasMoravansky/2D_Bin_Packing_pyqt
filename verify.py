#!/usr/bin/env python3
"""Validate Python version, dependencies, and core imports for reproducible setup."""

from __future__ import annotations

import importlib
import sys


def main() -> int:
    if sys.version_info < (3, 10):
        print("FAIL: Python 3.10+ required, got", sys.version)
        return 1
    print("OK Python", sys.version.split()[0])

    for name in ("PyQt5", "pytest"):
        try:
            m = importlib.import_module(name)
            ver = getattr(m, "__version__", "unknown")
            print(f"OK {name} {ver}")
        except Exception as e:
            print(f"FAIL import {name}: {e}")
            return 1

    try:
        import src.domain  # noqa: F401
        import src.geometry  # noqa: F401
        import src.validation  # noqa: F401
        import src.solver  # noqa: F401
        import App.main  # noqa: F401
        print("OK project packages import")
    except Exception as e:
        print("FAIL project import:", e)
        return 1

    print("verify.py: all checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
