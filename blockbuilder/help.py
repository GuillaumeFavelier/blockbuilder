"""Module about basic help."""

from qtpy.QtWidgets import QDialog


class HelpDialog(QDialog):
    """Display basic help."""

    def __init__(self, parent=None):
        super().__init__(parent)
