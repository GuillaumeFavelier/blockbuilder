import os
from PyQt5.QtWidgets import QApplication
from blockbuilder.builder import Builder


def main(testing=False):
    """Start BlockBuilder application."""
    if not testing:
        app = QApplication([''])
    builder = Builder(testing=testing)
    if testing:
        return builder
    else:
        app.exec_()
        return None


if __name__ == "__main__":
    testing = os.environ.get("BB_TESTING", False)
    main(testing)
