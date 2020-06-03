from PyQt5.QtWidgets import QApplication
from blockbuilder import __version__
from blockbuilder.builder import Builder
from blockbuilder.params import rcParams


def main(testing=False):
    """Start BlockBuilder application."""
    if not testing:
        app = QApplication([''])
    builder = Builder(testing=testing)
    app_name = rcParams["app"]["name"]
    title = app_name + ' - ' + __version__
    builder.setWindowTitle(title)
    if testing:
        return builder
    else:
        app.exec_()
        return None


if __name__ == "__main__":
    main()
