"""Module about basic help."""

from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton


class HelpDialog(QDialog):
    """Display basic help."""

    def __init__(self, icons, icon_size, short_desc, long_desc, parent=None):
        """Initialize the HelpDialog."""
        super().__init__(parent)

        assert len(icons.values()) == len(short_desc) == len(long_desc)

        layout = QGridLayout()
        for idx, icon in enumerate(icons.values()):
            pix = QPixmap(icon.pixmap(*icon_size))
            label = QLabel()
            label.setPixmap(pix)
            layout.addWidget(label, idx, 0)
            layout.addWidget(QLabel('<b>' + short_desc[idx] + '</b>'), idx, 1)
            layout.addWidget(QLabel(long_desc[idx]), idx, 2)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.close)
        layout.addWidget(self.ok_button, idx + 1, 0, 1, 3)

        self.setWindowTitle("Help")
        self.setModal(True)
        self.setLayout(layout)
