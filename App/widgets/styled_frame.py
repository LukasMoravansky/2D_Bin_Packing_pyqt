from __future__ import annotations

from PyQt5.QtWidgets import QFrame


class StyledFrame(QFrame):
    """Primary card panel: 14px radius, 1px soft border, BG_PANEL."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("styledFramePrimary")
        self.setFrameShape(QFrame.StyledPanel)
