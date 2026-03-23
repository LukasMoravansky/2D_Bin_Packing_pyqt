from __future__ import annotations

import logging
from typing import Protocol


class _EmitStr(Protocol):
    def emit(self, s: str) -> None: ...


_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
_DATE_FORMAT = "%H:%M:%S"


def configure_logging(gui_emit: _EmitStr | None = None) -> None:
    """Attach root logger with console handler; optional Qt GUI bridge via signal."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
    root.addHandler(console)

    if gui_emit is not None:

        class QtLogHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                try:
                    msg = self.format(record)
                    gui_emit.emit(msg)
                except Exception:
                    self.handleError(record)

        gui_handler = QtLogHandler()
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        root.addHandler(gui_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
