import pytest

from PyQt5 import QtCore

from blockbuilder.params import rcParams
from blockbuilder.interactive_plotter import InteractivePlotter

event_delay = 150


def test_interactive_plotter(qtbot):
    plotter = InteractivePlotter(params=rcParams)
    qtbot.addWidget(plotter)
    plotter.show()
    keys = [
        rcParams["keybinding"]["azimuth_minus"]["value"],
        rcParams["keybinding"]["azimuth_plus"]["value"],
        rcParams["keybinding"]["elevation_minus"]["value"],
        rcParams["keybinding"]["elevation_plus"]["value"],
        rcParams["keybinding"]["distance_plus"]["value"],
        rcParams["keybinding"]["distance_minus"]["value"],
    ]
    for key in keys:
        qtbot.keyPress(
            plotter.render_widget,
            _parse_key(key),
            QtCore.Qt.NoModifier,
            event_delay,
        )

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
