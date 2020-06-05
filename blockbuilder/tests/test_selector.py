from contextlib import contextmanager
import numpy as np
from blockbuilder.utils import _hasattr
from blockbuilder.selector import (Selector, AreaSelector, Symmetry,
                                   SymmetrySelector)


def test_selector():
    selector = Selector()
    assert all(np.equal(selector.dimensions, [2, 2, 2]))
    assert _hasattr(selector, "coords", type(None))
    assert _hasattr(selector, "coords_type", type)
    assert selector.selection() is None

    # requires an actor (i.e. plotter)
    # selector.hide()
    # selector.show()

    coords = np.asarray([0, 0, 0])
    selector.select(coords)
    assert all(np.equal(selector.selection(), coords))


def test_area_selector():
    selector = AreaSelector()
    assert _hasattr(selector, "area", type(None))
    assert _hasattr(selector, "area_first_coords", type(None))
    assert _hasattr(selector, "area_last_coords", type(None))

    # test with a valid area (min, max):
    area = np.asarray([[0, 0, 0], [1, 1, 1]])
    with enabled_area_testing(selector, area):
        selected_area = np.asarray(selector.selection_area())
        assert all(np.equal(selected_area.flatten(), area.flatten()))


def test_symmetry_selector():
    dimensions = [3, 3, 3]
    selector = SymmetrySelector(dimensions=dimensions)
    assert _hasattr(selector, "selector_x", AreaSelector)
    assert _hasattr(selector, "selector_y", AreaSelector)
    assert _hasattr(selector, "selector_xy", AreaSelector)
    assert _hasattr(selector, "symmetry", Symmetry)
    assert _hasattr(selector, "dimensions", np.ndarray)

    for symmetry in Symmetry:
        selector.set_symmetry(symmetry)
        # test with a valid area (min, max):
        area = np.asarray([[0, 0, 0], [1, 1, 1]])
        diff_area = area[1] - area[0]
        with enabled_area_testing(selector, area):
            selected_area = np.asarray(selector.selection_area())
            assert all(np.equal(selected_area[0].flatten(), area.flatten()))
            for sym_area in selected_area:
                diff_sym_area = sym_area[1] - sym_area[0]
                assert all(np.equal(diff_sym_area, diff_area))
        coords = np.asarray([0, 0, 0])
        selected = selector.selection()
        assert all(np.equal(selected[0], coords))

    # requires an actor (i.e. plotter)
    # selector.hide()
    # selector.show()


@contextmanager
def enabled_area_testing(selector, area):
    selector.set_first_coords(area[0])
    assert all(np.equal(selector.get_first_coords(), area[0]))
    selector.set_last_coords(area[1])
    assert all(np.equal(selector.get_last_coords(), area[1]))
    selector.select_area(area)
    assert selector.area_first_coords is not None
    assert selector.area_last_coords is not None
    try:
        yield
    finally:
        selector.reset_area()
        assert selector.area_first_coords is None
        assert selector.area_last_coords is None
