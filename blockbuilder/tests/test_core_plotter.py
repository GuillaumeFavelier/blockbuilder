from blockbuilder.params import rcParams
from blockbuilder.utils import _hasattr, get_poly_data, get_uniform_grid
from blockbuilder.core_plotter import CorePlotter


def test_core_plotter(qtbot):
    black = (0, 0, 0)
    white = (1, 1, 1)
    # default parameters
    mesh = get_poly_data()
    # We set advanced=True in here but on Azure (and GA),
    # AA and smoothing cause segfaults (access violation) on
    # grid datasets. So we use PolyData but this is basically
    # calculated risk.
    plotter = CorePlotter(params=rcParams, advanced=True, testing=False)
    assert _hasattr(plotter, "params", dict)
    assert _hasattr(plotter, "show_edges", bool)
    assert _hasattr(plotter, "line_width", int)
    assert _hasattr(plotter, "window_size", list)
    assert _hasattr(plotter, "advanced", bool)
    assert _hasattr(plotter, "background_top_color", list)
    assert _hasattr(plotter, "background_bottom_color", list)
    qtbot.addWidget(plotter)
    plotter.set_background(color=black)
    plotter.set_background(color=black, top=white)
    plotter.show()
    plotter.add_mesh(mesh, rgba=True)
    plotter.add_mesh(mesh, rgba=False)
    plotter.reset_camera()
    plotter.close()

    # modified parameters
    mesh = get_uniform_grid()
    window_size = (300, 300)
    background_bottom_color = (0, 0, 0)
    background_top_color = (1, 1, 1)
    # we use advanced=False and testing=False)for coverage:
    plotter = CorePlotter(
        params=rcParams,
        window_size=window_size,
        background_top_color=background_top_color,
        background_bottom_color=background_bottom_color,
        advanced=False,
        testing=False,
    )
    qtbot.addWidget(plotter)
    plotter.show()
    plotter.close()
