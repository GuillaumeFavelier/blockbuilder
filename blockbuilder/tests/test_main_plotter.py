import numpy as np
from blockbuilder.utils import _hasattr
from blockbuilder.block import Block
from blockbuilder.grid import Grid
from blockbuilder.plane import Plane
from blockbuilder.selector import Symmetry, SymmetrySelector
from blockbuilder.main_plotter import MainPlotter, BlockMode, Action, Toggle
from PyQt5 import QtCore


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


def test_main_plotter_add_block(qtbot):
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)

    # add a block
    plotter.set_block_mode(BlockMode.BUILD)
    window_size = plotter.window_size
    qtbot.mouseMove(plotter.render_widget,
                    QtCore.QPoint(window_size[0] // 2, window_size[1] // 2))
    qtbot.mouseClick(plotter.render_widget, QtCore.Qt.LeftButton)

    # remove a block
    plotter.set_block_mode(BlockMode.DELETE)
    qtbot.mouseMove(plotter.render_widget,
                    QtCore.QPoint(window_size[0] // 2, window_size[1] // 2))
    qtbot.mouseClick(plotter.render_widget, QtCore.Qt.LeftButton)

    plotter.close()


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
