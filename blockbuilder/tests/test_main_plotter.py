import os
import numpy as np
import pytest
from blockbuilder.params import rcParams
from blockbuilder.utils import _hasattr
from blockbuilder.block import Block
from blockbuilder.grid import Grid
from blockbuilder.plane import Plane
from blockbuilder.selector import Symmetry, SymmetrySelector
from blockbuilder.main_plotter import (MainPlotter, BlockMode, Action, Toggle,
                                       _get_toolbar_area, _rgb2str, _qrgb2rgb)
from PyQt5 import QtCore
from PyQt5.QtGui import QColor

# testing dimensions
rcParams["builder"]["dimensions"] = (8, 8, 8)
event_delay = 300


def test_main_plotter(qtbot):
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)

    _hasattr(plotter, "unit", float)
    _hasattr(plotter, "default_block_color", tuple)
    _hasattr(plotter, "toolbar_area", str)
    _hasattr(plotter, "icon_size", tuple)
    _hasattr(plotter, "dimensions", tuple)
    _hasattr(plotter, "button_pressed", bool)
    _hasattr(plotter, "button_released", bool)
    _hasattr(plotter, "area_selection", bool)
    _hasattr(plotter, "floor", type(None))
    _hasattr(plotter, "ceiling", type(None))
    _hasattr(plotter, "icons", type(None))
    _hasattr(plotter, "toolbar", type(None))
    _hasattr(plotter, "current_block_mode", type(None))
    _hasattr(plotter, "mode_functions", type(None))

    # block mode
    assert plotter.current_block_mode == BlockMode.BUILD
    assert isinstance(plotter.mode_functions, dict)
    assert len(plotter.mode_functions.keys()) == len(BlockMode)

    # load icons
    for category in (BlockMode, Action, Toggle, Symmetry):
        for element in category:
            assert element in plotter.icons
            assert plotter.icons[element] is not None

    # toolbar is hard to test
    assert plotter.toolbar is not None

    # load elements
    assert _hasattr(plotter, "block", Block)
    assert _hasattr(plotter, "grid", Grid)
    assert _hasattr(plotter, "plane", Plane)
    assert _hasattr(plotter, "selector", SymmetrySelector)

    # add elements
    for element_name in ["block", "grid", "plane", "selector"]:
        element = getattr(plotter, element_name)
        assert element.actor is not None
        assert element.actor.element_id == element.element_id
    for selector_name in ["x", "y", "xy"]:
        selector = getattr(plotter.selector, "selector_" + selector_name)
        assert selector.actor is not None
        assert selector.actor.element_id == selector.element_id

    # remove elements
    plotter.remove_elements()
    for element_name in ["block", "grid", "plane", "selector"]:
        element = getattr(plotter, element_name)
        assert element.actor is None
    for selector_name in ["x", "y", "xy"]:
        selector = getattr(plotter.selector, "selector_" + selector_name)
        assert selector.actor is None

    plotter.close()


def test_main_plotter_actions(qtbot, tmpdir):
    output_dir = str(tmpdir.mkdir("tmpdir"))
    assert os.path.isdir(output_dir)
    filename = str(os.path.join(output_dir, "tmp.vtk"))

    # export blockset
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)
    plotter.action_export(filename)
    with pytest.raises(TypeError, match="filename"):
        plotter.action_export(-1)
    plotter.close()

    # import blockset
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)
    plotter.action_import(filename)
    with pytest.raises(TypeError, match="filename"):
        plotter.action_import(-1)

    # reset
    plotter.action_reset(None)

    plotter.close()


def test_main_plotter_toggles(qtbot):
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)
    for toggle in Toggle:
        func_name = 'toggle_' + toggle.name.lower()
        func = getattr(plotter, func_name)
        for value in [True, False]:
            func(value)
    plotter.close()


def test_main_plotter_block_scenario(qtbot):
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)
    window_size = plotter.window_size
    point = QtCore.QPoint(window_size[0] // 2, window_size[1] // 2)
    plotter.set_symmetry(Symmetry.SYMMETRY_XY)
    plotter.toggle_select(False)

    # add one block
    plotter.set_block_mode(BlockMode.BUILD)
    qtbot.mouseMove(plotter.render_widget, point, event_delay)
    qtbot.mousePress(plotter.render_widget, QtCore.Qt.LeftButton,
                     QtCore.Qt.NoModifier, point, event_delay)
    qtbot.mouseRelease(plotter.render_widget, QtCore.Qt.LeftButton,
                       QtCore.Qt.NoModifier, point, event_delay)

    # remove one block
    plotter.set_block_mode(BlockMode.DELETE)
    qtbot.mousePress(plotter.render_widget, QtCore.Qt.LeftButton,
                     QtCore.Qt.NoModifier, point, event_delay)
    qtbot.mouseRelease(plotter.render_widget, QtCore.Qt.LeftButton,
                       QtCore.Qt.NoModifier, point, event_delay)
    plotter.close()


def test_main_plotter_area_scenario(qtbot):
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)
    window_size = plotter.window_size
    start_point = QtCore.QPoint(window_size[0] // 2, window_size[1] // 2)
    end_point = QtCore.QPoint(window_size[0] // 2 + 100,
                              window_size[1] // 2 + 100)
    plotter.set_symmetry(Symmetry.SYMMETRY_XY)
    plotter.toggle_select(True)

    # add one block
    plotter.set_block_mode(BlockMode.BUILD)
    qtbot.mouseMove(plotter.render_widget, start_point, event_delay)
    qtbot.mousePress(plotter.render_widget, QtCore.Qt.LeftButton,
                     QtCore.Qt.NoModifier, start_point, event_delay)
    qtbot.mouseRelease(plotter.render_widget, QtCore.Qt.LeftButton,
                       QtCore.Qt.NoModifier, start_point, event_delay)

    # remove one block
    plotter.set_block_mode(BlockMode.DELETE)
    qtbot.mousePress(plotter.render_widget, QtCore.Qt.LeftButton,
                     QtCore.Qt.NoModifier, start_point, event_delay)
    qtbot.mouseRelease(plotter.render_widget, QtCore.Qt.LeftButton,
                       QtCore.Qt.NoModifier, start_point, event_delay)

    # add a set of blocks
    plotter.set_block_mode(BlockMode.BUILD)
    qtbot.mouseMove(plotter.render_widget, start_point, event_delay)
    qtbot.mousePress(plotter.render_widget, QtCore.Qt.LeftButton,
                     QtCore.Qt.NoModifier, start_point, event_delay)
    qtbot.mouseMove(plotter.render_widget, end_point, event_delay)
    qtbot.mouseRelease(plotter.render_widget, QtCore.Qt.LeftButton,
                       QtCore.Qt.NoModifier, end_point, event_delay)

    # remove a set of blocks
    plotter.set_block_mode(BlockMode.DELETE)
    qtbot.mousePress(plotter.render_widget, QtCore.Qt.LeftButton,
                     QtCore.Qt.NoModifier, end_point, event_delay)
    qtbot.mouseMove(plotter.render_widget, start_point, event_delay)
    qtbot.mouseRelease(plotter.render_widget, QtCore.Qt.LeftButton,
                       QtCore.Qt.NoModifier, start_point, event_delay)


def test_main_plotter_move_camera(qtbot):
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)

    # camera
    plotter.move_camera(update="distance")
    tr = [0, 0, 1]
    grid_center = plotter.grid.center
    plotter.translate_camera(tr)
    assert np.allclose(plotter.camera.GetFocalPoint(), grid_center + tr)
    plotter.update_camera()
    assert np.allclose(plotter.camera.GetFocalPoint(), plotter.grid.center)

    plotter.close()


def test_main_plotter_coverage(qtbot):
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)
    # just for coverage:
    plotter.set_block_mode()
    for symmetry in Symmetry:
        plotter.set_symmetry(symmetry)
        plotter.selector.hide()
        plotter.selector.show()

    # no mouse wheel event in pytest-qt
    plotter.on_mouse_wheel_forward(None, None)
    plotter.on_mouse_wheel_backward(None, None)
    # corner cases
    plotter.grid.origin[2] = plotter.ceiling + 1
    plotter.on_mouse_wheel_forward(None, None)
    plotter.grid.origin[2] = plotter.floor - 1
    plotter.on_mouse_wheel_backward(None, None)

    plotter.close()


def test_get_toolbar_area():
    toolbar_areas = rcParams["app"]["toolbar"]["areas"]
    for area in toolbar_areas:
        _get_toolbar_area(area)
    with pytest.raises(TypeError, match="type"):
        _get_toolbar_area(-1)
    with pytest.raises(ValueError, match="area"):
        _get_toolbar_area("foo")


def test_rgb2str():
    white = (1., 1., 1.)
    assert isinstance(_rgb2str(white, is_int=False), str)
    white = (255, 255, 255)
    assert isinstance(_rgb2str(white, is_int=True), str)


def test_qrgb2rgb():
    white = QColor(255, 255, 255)
    assert isinstance(_qrgb2rgb(white), tuple)
