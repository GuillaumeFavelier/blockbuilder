import vtk
from blockbuilder.utils import _hasattr
from blockbuilder.core_plotter import CorePlotter


def get_poly_data():
    mesh = vtk.vtkSphereSource()
    mesh.SetPhiResolution(8)
    mesh.SetThetaResolution(8)
    return mesh.GetOutput()


def get_uniform_grid():
    mesh = vtk.vtkUniformGrid()
    mesh.Initialize()
    mesh.SetDimensions(2, 2, 2)
    mesh.SetSpacing(1, 1, 1)
    mesh.SetOrigin(0, 0, 0)
    return mesh


def test_core_plotter(qtbot):
    black = (0, 0, 0)
    white = (1, 1, 1)
    # default parameters
    mesh = get_poly_data()
    # We set advanced=True in here but on Azure (and GA),
    # AA and smoothing cause segfaults (access violation) on
    # grid datasets. So we use PolyData but this is basically
    # calculated risk.
    plotter = CorePlotter(advanced=True, testing=False)
    assert _hasattr(plotter, "show_edges", bool)
    assert _hasattr(plotter, "line_width", int)
    assert _hasattr(plotter, "window_size", tuple)
    assert _hasattr(plotter, "advanced", bool)
    assert _hasattr(plotter, "background_top_color", tuple)
    assert _hasattr(plotter, "background_bottom_color", tuple)
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
        window_size=window_size,
        background_top_color=background_top_color,
        background_bottom_color=background_bottom_color,
        advanced=False,
        testing=False,
    )
    qtbot.addWidget(plotter)
    plotter.show()
    plotter.close()
