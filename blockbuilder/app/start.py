from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication
from blockbuilder import __version__
from blockbuilder.icons import resources
from blockbuilder.params import get_params
from blockbuilder.main_plotter import MainPlotter


def main(testing=False):
    """Start BlockBuilder application."""
    if not testing:
        app = QApplication([''])
    resources.qInitResources()
    params = get_params()
    app_name = params["app"]["name"]
    app_icon_name = params["app"]["icon"]
    plotter = MainPlotter(params=params, testing=testing)
    title = app_name + ' - ' + __version__
    plotter.setWindowTitle(title)
    icon = QIcon(':/' + app_icon_name)
    plotter.setWindowIcon(icon)
    if testing:
        return plotter
    app.exec_()


if __name__ == "__main__":
    main()
