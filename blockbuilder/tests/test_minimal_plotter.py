import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from blockbuilder.utils import _hasattr
from blockbuilder.minimal_plotter import MinimalPlotter


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
