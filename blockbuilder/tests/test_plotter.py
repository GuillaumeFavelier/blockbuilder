import os
import pytest
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from blockbuilder.plotter import MinimalPlotter, CorePlotter, Plotter


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


@pytest.mark.skipif(os.environ.get("AZURE_CI_LINUX", False),
                    reason="Bug with pyvirtualdisplay")
def test_minimal_plotter(qtbot):
    plotter = MinimalPlotter()
    assert _hasattr(plotter, "render_widget", QVTKRenderWindowInteractor)
    assert _hasattr(plotter, "render_window", vtk.vtkRenderWindow)
    assert _hasattr(plotter, "renderer", vtk.vtkRenderer)
    assert _hasattr(plotter, "camera", vtk.vtkCamera)
    assert _hasattr(plotter, "interactor", vtk.vtkRenderWindowInteractor)
    qtbot.addWidget(plotter)
    assert not plotter.isVisible()
    plotter.show()
    assert plotter.isVisible()
    plotter.close()


@pytest.mark.skipif(os.environ.get("AZURE_CI_LINUX", False),
                    reason="Bug with pyvirtualdisplay")
def test_core_plotter(qtbot):
    black = (0, 0, 0)
    white = (1, 1, 1)
    mesh = get_uniform_grid()
    plotter = CorePlotter()
    assert _hasattr(plotter, "show_edges", bool)
    assert _hasattr(plotter, "line_width", int)
    qtbot.addWidget(plotter)
    plotter.set_background(color=black)
    plotter.set_background(color=black, top=white)
    # we disable AA and smoothing for Azure
    plotter.set_anti_aliasing(False)
    plotter.set_line_smoothing(False)
    plotter.set_polygon_smoothing(False)
    plotter.set_style(None)
    plotter.reset_camera()
    plotter.show()
    plotter.add_mesh(mesh, rgba=True)
    plotter.add_mesh(mesh, rgba=False)
    plotter.render_scene()
    plotter.close()


@pytest.mark.skipif(os.environ.get("AZURE_CI_LINUX", False),
                    reason="Bug with pyvirtualdisplay")
def test_plotter(qtbot):
    # default parameters
    mesh = get_poly_data()
    # We set advanced=True in here but on Azure (and GA),
    # AA and smoothing cause segfaults (access violation) on
    # grid datasets. So we use PolyData but this is basically
    # calculated risk.
    plotter = Plotter(advanced=True, testing=False)
    assert _hasattr(plotter, "window_size", tuple)
    assert _hasattr(plotter, "advanced", bool)
    assert _hasattr(plotter, "background_top_color", tuple)
    assert _hasattr(plotter, "background_bottom_color", tuple)
    qtbot.addWidget(plotter)
    plotter.show()
    plotter.add_mesh(mesh)
    plotter.close()

    # modified parameters
    mesh = get_uniform_grid()
    window_size = (300, 300)
    background_bottom_color = (0, 0, 0)
    background_top_color = (1, 1, 1)
    # we use advanced=False and testing=False)for coverage:
    plotter = Plotter(
        window_size=window_size,
        background_top_color=background_top_color,
        background_bottom_color=background_bottom_color,
        advanced=False,
        testing=False,
    )
    qtbot.addWidget(plotter)
    plotter.show()
    plotter.close()


def _hasattr(variable, attribute_name, variable_type):
    if not hasattr(variable, attribute_name):
        return False
    return isinstance(getattr(variable, attribute_name), variable_type)
