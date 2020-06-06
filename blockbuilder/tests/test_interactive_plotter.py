import pytest
from blockbuilder.interactive_plotter import InteractivePlotter
from blockbuilder.params import rcParams
from PyQt5 import QtCore


def test_interactive_plotter(qtbot):
    plotter = InteractivePlotter()
    qtbot.addWidget(plotter)
    plotter.show()
    keys = [
        rcParams["keybinding"]["azimuth_minus"],
        rcParams["keybinding"]["azimuth_plus"],
        rcParams["keybinding"]["elevation_minus"],
        rcParams["keybinding"]["elevation_plus"],
        rcParams["keybinding"]["distance_plus"],
        rcParams["keybinding"]["distance_minus"],
    ]
    for key in keys:
        qtbot.keyPress(plotter.render_widget, _parse_key(key))

    plotter.translate_camera([0, 0, 0])

    # check boundaries
    plotter.azimuth = plotter.azimuth_rng[0]
    plotter.move_camera(update="azimuth", inverse=False)
    plotter.azimuth = plotter.azimuth_rng[1]
    plotter.move_camera(update="azimuth")
    with pytest.raises(ValueError, match=r'update'):
        plotter.move_camera(update="foo")
    plotter.close()


def _parse_key(key):
    if key == 'Up':
        return QtCore.Qt.Key.Key_Up
    elif key == 'Down':
        return QtCore.Qt.Key.Key_Down
    else:
        return key
