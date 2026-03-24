from __future__ import annotations

import sys
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox

from App.app_logging import get_logger
from App.main_window import MainWindow

_LOG = get_logger("packing.gui")

APPLICATION_STYLESHEET = """
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
  font-family: "Inter", "Segoe UI", "SF Pro Text", sans-serif;
  font-size: 14px;
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
  font-size: 40px;
  font-weight: 600;
  color: #171A1C;
  letter-spacing: 0.2px;
  padding-bottom: 4px;
}
QLabel#cardTitle {
  font-size: 20px;
  font-weight: 600;
  color: #171A1C;
}
QLabel#sectionTitle {
  font-size: 20px;
  font-weight: 600;
  color: #171A1C;
}
QLabel#metricsLabel {
  font-size: 14px;
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
  font-size: 13px;
  font-family: "Cascadia Mono", "Consolas", "SF Mono", monospace;
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
  padding: 8px 8px;
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


def _excepthook(exc_type, exc, tb) -> None:
    text = "".join(traceback.format_exception(exc_type, exc, tb))
    _LOG.error("Unhandled exception:\n%s", text)
    try:
        QMessageBox.critical(None, "Unexpected error", str(exc))
    except Exception:
        pass


def main() -> None:
    sys.excepthook = _excepthook
    app = QApplication(sys.argv)
    app.setStyleSheet(APPLICATION_STYLESHEET)
    win = MainWindow()
    win.resize(1280, 800)
    win.show()
    _LOG.info("Application started.")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
