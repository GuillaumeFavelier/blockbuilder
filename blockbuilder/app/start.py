from PyQt5.QtWidgets import QApplication
from blockbuilder import __version__
from blockbuilder.params import get_params
from blockbuilder.main_plotter import MainPlotter


def main(testing=False):
    """Start BlockBuilder application."""
    if not testing:
        app = QApplication([''])
    params = get_params()
    app_name = params["app"]["name"]
    plotter = MainPlotter(params=params, testing=testing)
    title = app_name + ' - ' + __version__
    plotter.setWindowTitle(title)
    if testing:
        return plotter
    app.exec_()


if __name__ == "__main__":
    main()
