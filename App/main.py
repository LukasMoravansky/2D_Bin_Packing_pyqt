from __future__ import annotations

import sys
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox

from App.app_logging import get_logger
from App.main_window import MainWindow

_LOG = get_logger("packing.gui")

APPLICATION_STYLESHEET = """
QWidget {
  background-color: #EDEFF2;
  color: #161A16;
  font-family: "Segoe UI", "Inter", sans-serif;
  font-size: 14px;
}
QMainWindow, QSplitter, QFrame#styledFramePrimary {
  background-color: #F6F7F4;
}
QFrame#styledFramePrimary {
  background-color: #FBFBF9;
  border: 1px solid #DADDD6;
  border-radius: 14px;
}
QLabel#pageTitle {
  font-size: 32px;
  font-weight: 600;
  color: #161A16;
}
QLabel#cardTitle {
  font-size: 16px;
  font-weight: 600;
  color: #161A16;
}
QLabel#sectionTitle {
  font-size: 16px;
  font-weight: 600;
  color: #161A16;
}
QLabel#metricsLabel {
  font-size: 13px;
  color: #62685F;
}
QPlainTextEdit#logPlainText {
  background-color: #FBFBF9;
  border: 1px solid #DADDD6;
  border-radius: 10px;
  padding: 8px;
  color: #161A16;
  font-size: 13px;
}
QDoubleSpinBox, QSpinBox {
  min-height: 34px;
  padding: 4px 10px;
  border: 1px solid #CDD2CA;
  border-radius: 8px;
  background: #FFFFFF;
}
QDoubleSpinBox:hover, QSpinBox:hover {
  border: 1px solid #B8C0B4;
}
QDoubleSpinBox:focus, QSpinBox:focus {
  border: 1px solid #2469B2;
  background: #FDFEFE;
  selection-background-color: #D9E9FB;
  selection-color: #13263B;
}
QPushButton#btnPrimary {
  min-height: 40px;
  border-radius: 10px;
  font-weight: 600;
  color: #F2F4F1;
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #2E3130, stop:1 #1E201F);
  border: 1px solid #222524;
}
QPushButton#btnPrimary:hover {
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #383C3A, stop:1 #272A29);
}
QPushButton#btnPrimary:pressed {
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #262928, stop:1 #171918);
}
QPushButton#btnPrimary:disabled {
  background: #B8BCB6;
  color: #ECEEEA;
  border: 1px solid #AEB3AC;
}
QPushButton#btnSecondary {
  min-height: 36px;
  border-radius: 9px;
  font-weight: 600;
  color: #161A16;
  background: #F3F4F1;
  border: 1px solid #DADDD6;
}
QPushButton#btnSecondary:hover {
  background: #EEF0EB;
  border: 1px solid #C9CDC5;
}
QPushButton#btnSecondary:pressed {
  background: #E4E7E1;
  border: 1px solid #BCC1B9;
}
QTableWidget {
  background: #FFFFFF;
  alternate-background-color: #F8FAF7;
  border: 1px solid #CDD2CA;
  border-radius: 10px;
  gridline-color: #DEE3DB;
  selection-background-color: #E3EEF9;
  selection-color: #13263B;
}
QTableWidget::item {
  border: none;
  padding: 4px 6px;
}
QTableWidget::item:selected {
  background: #E3EEF9;
  color: #13263B;
}
QHeaderView::section {
  background: #EFF2EC;
  color: #4F564C;
  padding: 8px 6px;
  border: none;
  border-bottom: 1px solid #D4D9D0;
  font-weight: 600;
}
QCheckBox::indicator {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid #A9B1A5;
  background: #FFFFFF;
}
QCheckBox::indicator:hover {
  border: 1px solid #8D9788;
}
QCheckBox::indicator:checked {
  border: 1px solid #2469B2;
  background: #2469B2;
}
QScrollBar:vertical {
  width: 10px;
  margin: 0px;
  background: #F2F4F0;
  border-left: 1px solid #DEE3DB;
}
QScrollBar::handle:vertical {
  background: #BCC3B8;
  min-height: 28px;
  border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
  background: #A9B1A5;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
  height: 0px;
}
QScrollBar:horizontal {
  height: 10px;
  margin: 0px;
  background: #F2F4F0;
  border-top: 1px solid #DEE3DB;
}
QScrollBar::handle:horizontal {
  background: #BCC3B8;
  min-width: 28px;
  border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
  background: #A9B1A5;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
  width: 0px;
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
