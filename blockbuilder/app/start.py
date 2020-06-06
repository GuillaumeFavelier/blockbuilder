from PyQt5.QtWidgets import QApplication
from blockbuilder import __version__
from blockbuilder.main_plotter import MainPlotter
from blockbuilder.params import rcParams


def main(testing=False):
    """Start BlockBuilder application."""
    if not testing:
        app = QApplication([''])
    plotter = MainPlotter(testing=testing)
    app_name = rcParams["app"]["name"]
    title = app_name + ' - ' + __version__
    plotter.setWindowTitle(title)
    if testing:
        return plotter
    app.exec_()


if __name__ == "__main__":
    main()
