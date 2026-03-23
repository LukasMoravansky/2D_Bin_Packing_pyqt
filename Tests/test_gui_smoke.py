"""Minimal import/smoke test for GUI package (no display interaction)."""


def test_import_app_main() -> None:
    import App.main  # noqa: F401
