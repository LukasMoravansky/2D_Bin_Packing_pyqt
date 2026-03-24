from __future__ import annotations

import os
import sys
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox

from App.app_logging import get_logger
from App.main_window import MainWindow

_LOG = get_logger("packing.gui")

TYPOGRAPHY_PRESETS: dict[str, dict[str, str]] = {
    "executive_calm": {
        "ui_font_stack": '"Segoe UI", "Inter", "Arial", sans-serif',
        "base_font_size": "14px",
        "page_title_size": "42px",
        "page_title_weight": "600",
        "card_title_size": "22px",
        "card_title_weight": "600",
        "section_title_size": "22px",
        "section_title_weight": "600",
        "metrics_size": "14px",
        "metrics_weight": "400",
        "log_font_size": "13px",
        "log_font_stack": '"Cascadia Mono", "Consolas", "SF Mono", monospace',
    },
    "industrial_dense": {
        "ui_font_stack": '"Bahnschrift", "Segoe UI", "Arial", sans-serif',
        "base_font_size": "13px",
        "page_title_size": "38px",
        "page_title_weight": "600",
        "card_title_size": "19px",
        "card_title_weight": "600",
        "section_title_size": "19px",
        "section_title_weight": "600",
        "metrics_size": "13px",
        "metrics_weight": "400",
        "log_font_size": "12px",
        "log_font_stack": '"Consolas", "Lucida Console", "Courier New", monospace',
    },
    "enterprise_technical": {
        "ui_font_stack": '"Verdana", "Tahoma", "Segoe UI", sans-serif',
        "base_font_size": "14px",
        "page_title_size": "40px",
        "page_title_weight": "700",
        "card_title_size": "20px",
        "card_title_weight": "700",
        "section_title_size": "20px",
        "section_title_weight": "700",
        "metrics_size": "14px",
        "metrics_weight": "400",
        "log_font_size": "13px",
        "log_font_stack": '"Consolas", "Courier New", monospace',
    },
}

DEFAULT_TYPOGRAPHY_PRESET = "executive_calm"

APPLICATION_STYLESHEET_TEMPLATE = """
/* ===== Construction Control tokens =====
app bg: #F3F4F1
surface/card bg: #FFFFFF
soft bg: #ECEEEA
text primary: #171A1C
text muted: #5F666D
border soft: #E2E5E1
accent green: #BFDFA8
accent dark: #232629
======================================== */
QWidget {
  background: transparent;
  color: #171A1C;
  font-family: __UI_FONT_STACK__;
  font-size: __BASE_FONT_SIZE__;
}
QMainWindow, QWidget#appRoot, QSplitter {
  background-color: #F3F4F1;
}
QFrame#styledFramePrimary {
  background-color: #FFFFFF;
  border: 1px solid #E2E5E1;
  border-radius: 16px;
}
QFrame#styledFramePrimary > QWidget {
  background: transparent;
  border: none;
}
QLabel {
  background: transparent;
}
QLabel#pageTitle {
  font-size: __PAGE_TITLE_SIZE__;
  font-weight: __PAGE_TITLE_WEIGHT__;
  color: #171A1C;
  letter-spacing: 0.2px;
  padding-bottom: 4px;
}
QLabel#cardTitle {
  font-size: __CARD_TITLE_SIZE__;
  font-weight: __CARD_TITLE_WEIGHT__;
  color: #171A1C;
}
QLabel#sectionTitle {
  font-size: __SECTION_TITLE_SIZE__;
  font-weight: __SECTION_TITLE_WEIGHT__;
  color: #171A1C;
}
QLabel#metricsLabel {
  font-size: __METRICS_SIZE__;
  font-weight: __METRICS_WEIGHT__;
  color: #5F666D;
  line-height: 1.5;
  padding-top: 8px;
  padding-bottom: 8px;
}
QPlainTextEdit#logPlainText {
  background-color: #FFFFFF;
  border: 1px solid #E2E5E1;
  border-radius: 12px;
  padding: 10px 12px;
  color: #171A1C;
  font-size: __LOG_FONT_SIZE__;
  font-family: __LOG_FONT_STACK__;
}
QDoubleSpinBox, QSpinBox {
  min-height: 30px;
  padding: 2px 10px;
  border: 1px solid #E2E5E1;
  border-radius: 10px;
  background: #FFFFFF;
}
QDoubleSpinBox:hover, QSpinBox:hover {
  border: 1px solid #D2D7D2;
}
QDoubleSpinBox:focus, QSpinBox:focus {
  border: 1px solid #BFDFA8;
  background: #FFFFFF;
  selection-background-color: #DCECD1;
  selection-color: #171A1C;
}
QPushButton#btnPrimary {
  min-height: 40px;
  border-radius: 10px;
  font-weight: 600;
  color: #F3F4F1;
  background: #232629;
  border: 1px solid #232629;
}
QPushButton#btnPrimary:hover {
  background: #2B2F33;
  border: 1px solid #2B2F33;
}
QPushButton#btnPrimary:pressed {
  background: #1D2023;
  border: 1px solid #1D2023;
}
QPushButton#btnPrimary:disabled {
  background: #BFC4BF;
  color: #ECEEEA;
  border: 1px solid #BFC4BF;
}
QPushButton#btnSecondary {
  min-height: 38px;
  border-radius: 10px;
  font-weight: 600;
  color: #171A1C;
  background: #FFFFFF;
  border: 1px solid #E2E5E1;
}
QPushButton#btnSecondary:hover {
  background: #F6F7F4;
  border: 1px solid #D5DAD6;
}
QPushButton#btnSecondary:pressed {
  background: #ECEEEA;
  border: 1px solid #D0D5D1;
}
QPushButton#btnSecondary:disabled {
  color: #9AA19A;
  background: #F5F6F4;
  border: 1px solid #E2E5E1;
}
QGraphicsView#packingView {
  background: #ECEEEA;
  border: 1px solid #E2E5E1;
  border-radius: 12px;
}
QGraphicsView#packingView QWidget {
  background: transparent;
}
QTableWidget {
  background: #FFFFFF;
  alternate-background-color: #F7F8F6;
  border: 1px solid #E2E5E1;
  border-radius: 12px;
  gridline-color: #EAECE8;
  selection-background-color: #E6F0DD;
  selection-color: #171A1C;
}
QTableWidget::item {
  border: none;
  padding: 0px 8px;
}
QTableWidget::item:selected {
  background: #E6F0DD;
  color: #171A1C;
}
QHeaderView::section {
  background: #F2F4F1;
  color: #5F666D;
  padding: 10px 8px;
  border: none;
  border-bottom: 1px solid #E2E5E1;
  font-weight: 600;
}
QCheckBox::indicator {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid #B5BCB6;
  background: #FFFFFF;
}
QCheckBox::indicator:hover {
  border: 1px solid #A4ABA5;
}
QCheckBox::indicator:checked {
  border: 1px solid #232629;
  background: #232629;
}
QSplitter::handle {
  background: #E2E5E1;
}
QSplitter::handle:horizontal {
  width: 2px;
}
QSplitter::handle:vertical {
  height: 2px;
}
QScrollBar:vertical {
  width: 8px;
  margin: 0px;
  background: transparent;
  border: none;
}
QScrollBar::handle:vertical {
  background: #C8CDC8;
  min-height: 28px;
  border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
  background: #B8BEB8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
  height: 0px;
  background: transparent;
}
QScrollBar:horizontal {
  height: 8px;
  margin: 0px;
  background: transparent;
  border: none;
}
QScrollBar::handle:horizontal {
  background: #C8CDC8;
  min-width: 28px;
  border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
  background: #B8BEB8;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
  width: 0px;
  background: transparent;
}
QAbstractScrollArea {
  background: transparent;
}
QAbstractScrollArea > QWidget#qt_scrollarea_viewport {
  background: transparent;
}
"""

def _build_stylesheet(preset_name: str) -> str:
    preset = TYPOGRAPHY_PRESETS.get(preset_name, TYPOGRAPHY_PRESETS[DEFAULT_TYPOGRAPHY_PRESET])
    stylesheet = APPLICATION_STYLESHEET_TEMPLATE
    token_map = {
        "__UI_FONT_STACK__": preset["ui_font_stack"],
        "__BASE_FONT_SIZE__": preset["base_font_size"],
        "__PAGE_TITLE_SIZE__": preset["page_title_size"],
        "__PAGE_TITLE_WEIGHT__": preset["page_title_weight"],
        "__CARD_TITLE_SIZE__": preset["card_title_size"],
        "__CARD_TITLE_WEIGHT__": preset["card_title_weight"],
        "__SECTION_TITLE_SIZE__": preset["section_title_size"],
        "__SECTION_TITLE_WEIGHT__": preset["section_title_weight"],
        "__METRICS_SIZE__": preset["metrics_size"],
        "__METRICS_WEIGHT__": preset["metrics_weight"],
        "__LOG_FONT_SIZE__": preset["log_font_size"],
        "__LOG_FONT_STACK__": preset["log_font_stack"],
    }
    for token, value in token_map.items():
        stylesheet = stylesheet.replace(token, value)
    return stylesheet


def _excepthook(exc_type, exc, tb) -> None:
    text = "".join(traceback.format_exception(exc_type, exc, tb))
    _LOG.error("Unhandled exception:\n%s", text)
    try:
        QMessageBox.critical(None, "Unexpected error", str(exc))
    except Exception:
        pass


def main() -> None:
    sys.excepthook = _excepthook
    preset_name = os.getenv("PACKING_UI_FONT_PRESET", DEFAULT_TYPOGRAPHY_PRESET).strip().lower()
    if preset_name not in TYPOGRAPHY_PRESETS:
        _LOG.warning(
            "Unknown PACKING_UI_FONT_PRESET '%s'. Falling back to '%s'.",
            preset_name,
            DEFAULT_TYPOGRAPHY_PRESET,
        )
        preset_name = DEFAULT_TYPOGRAPHY_PRESET
    app = QApplication(sys.argv)
    app.setStyleSheet(_build_stylesheet(preset_name))
    win = MainWindow()
    win.resize(1280, 800)
    win.show()
    _LOG.info("Typography preset selected: %s", preset_name)
    _LOG.info("Application started.")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
