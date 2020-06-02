from PyQt5.QtWidgets import QApplication
from blockbuilder.builder import Builder


def main():
    """Start BlockBuilder application."""
    app = QApplication([''])
    Builder()
    app.exec_()


if __name__ == "__main__":
    main()
