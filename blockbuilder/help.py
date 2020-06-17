"""Module about basic help."""

from qtpy.QtWidgets import QDialog


class HelpDialog(QDialog):
    """Display basic help."""

    def __init__(self, parent=None):
        """Initialize the HelpDialog."""
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.setModal(True)
