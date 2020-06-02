from blockbuilder.plotter import MinimalPlotter, CorePlotter, Plotter
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class FakeMesh(vtk.vtkStructuredGrid):
    def __init__(self):
        super().__init__()


def test_minimal_plotter(qtbot):
    plotter = MinimalPlotter()
    assert _hasattr(plotter, "render_widget", QVTKRenderWindowInteractor)
    assert _hasattr(plotter, "render_window", vtk.vtkRenderWindow)
    assert _hasattr(plotter, "renderer", vtk.vtkRenderer)
    assert _hasattr(plotter, "camera", vtk.vtkCamera)
    assert _hasattr(plotter, "interactor", vtk.vtkRenderWindowInteractor)
    qtbot.addWidget(plotter)
    assert not plotter.isVisible()
    plotter.start()
    assert plotter.isVisible()
    plotter.close()
    assert plotter.render_widget is None
    assert plotter.render_window is None
    assert plotter.renderer is None
    assert plotter.camera is None
    assert plotter.interactor is None


def test_core_plotter(qtbot):
    black = (0, 0, 0)
    white = (1, 1, 1)
    mesh = FakeMesh()
    plotter = CorePlotter()
    qtbot.addWidget(plotter)
    plotter.set_background(color=black)
    plotter.set_background(color=black, top=white)
    for value in [False, True]:
        plotter.set_anti_aliasing(value)
        plotter.set_line_smoothing(value)
        plotter.set_polygon_smoothing(value)
    plotter.set_style(None)
    plotter.reset_camera()
    plotter.add_mesh(mesh, rgba=True)
    plotter.add_mesh(mesh, rgba=False)
    plotter.render()
    plotter.close()


def test_plotter(qtbot):
    mesh = FakeMesh()
    # default parameters
    plotter = Plotter()
    assert _hasattr(plotter, "window_size", tuple)
    assert _hasattr(plotter, "show_edges", bool)
    assert _hasattr(plotter, "line_width", int)
    assert _hasattr(plotter, "advanced", bool)
    assert _hasattr(plotter, "background_top_color", tuple)
    assert _hasattr(plotter, "background_bottom_color", tuple)
    qtbot.addWidget(plotter)
    plotter.add_mesh(mesh)
    plotter.close()

    # modified parameters
    window_size = (300, 300)
    show_edges = False
    line_width = 1
    advanced = False
    background_bottom_color = (0, 0, 0)
    background_top_color = (1, 1, 1)
    plotter = Plotter(
        window_size=window_size,
        show_edges=show_edges,
        line_width=line_width,
        background_top_color=background_top_color,
        background_bottom_color=background_bottom_color,
        advanced=advanced
    )
    qtbot.addWidget(plotter)
    plotter.close()


def _hasattr(variable, attribute_name, variable_type):
    if not hasattr(variable, attribute_name):
        return False
    return isinstance(getattr(variable, attribute_name), variable_type)
