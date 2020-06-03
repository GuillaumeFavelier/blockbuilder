"""Module about visual properties."""

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QMainWindow
from .params import rcParams


class MinimalPlotter(QMainWindow):
    """Minimal plotter."""

    def __init__(self, parent=None):
        """Initialize the MinimalPlotter."""
        super().__init__(parent=parent)
        self.render_widget = QVTKRenderWindowInteractor()
        self.setCentralWidget(self.render_widget)
        self.render_window = self.render_widget.GetRenderWindow()
        self.renderer = vtk.vtkRenderer()
        self.camera = self.renderer.GetActiveCamera()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = self.render_window.GetInteractor()

    def showEvent(self, event):
        """Prepare the context for 3d."""
        event.accept()
        self.render_widget.Initialize()

    def closeEvent(self, event):
        """Clear the context properly."""
        self.render_widget.Finalize()
        event.accept()


class CorePlotter(MinimalPlotter):
    """Plotter specialized in low-level operations."""

    def __init__(self, parent=None):
        """Initialize the Plotter."""
        super().__init__(parent=parent)
        self.show_edges = rcParams["plotter"]["show_edges"]
        self.line_width = rcParams["plotter"]["line_width"]

    def set_background(self, color, top=None):
        """Set the background color."""
        self.renderer.SetBackground(color)
        if top is None:
            self.renderer.GradientBackgroundOff()
        else:
            self.renderer.GradientBackgroundOn()
            self.renderer.SetBackground2(top)
        self.renderer.Modified()

    def set_anti_aliasing(self, value):
        """Enable/Disable anti-aliasing."""
        self.renderer.SetUseFXAA(value)
        self.renderer.Modified()

    def set_line_smoothing(self, value):
        """Enable/Disable line smoothing."""
        self.render_window.SetLineSmoothing(value)
        self.render_window.Modified()

    def set_polygon_smoothing(self, value):
        """Enable/Disable line smoothing."""
        self.render_window.SetPolygonSmoothing(value)
        self.render_window.Modified()

    def set_style(self, style):
        """Set the interactor style."""
        self.interactor.SetInteractorStyle(style)
        self.interactor.Modified()

    def reset_camera(self):
        """Reset the camera."""
        self.renderer.ResetCamera()
        self.renderer.Modified()

    def render_scene(self):
        """Render the scene."""
        # fix the clipping planes being too small
        rng = [0] * 6
        self.renderer.ComputeVisiblePropBounds(rng)
        self.renderer.ResetCameraClippingRange(rng)
        self.render_window.Render()

    def add_mesh(self, mesh, rgba=False, color=(1., 1., 1.), opacity=1.,
                 edge_color=(0., 0., 0.)):
        """Add a mesh to the scene."""
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(mesh)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        if rgba:
            mapper.SetColorModeToDirectScalars()
        prop = actor.GetProperty()
        prop.SetColor(color)
        prop.SetOpacity(opacity)
        prop.SetEdgeColor(edge_color)
        prop.SetLineWidth(self.line_width)
        prop.SetEdgeVisibility(self.show_edges)
        self.renderer.AddActor(actor)
        self.renderer.Modified()
        return actor


class Plotter(CorePlotter):
    """Main plotter."""

    def __init__(self, parent=None, window_size=None,
                 advanced=None, background_top_color=None,
                 background_bottom_color=None, testing=False):
        """Initialize the default visual properties."""
        super().__init__(parent=parent)
        if window_size is None:
            window_size = rcParams["plotter"]["window_size"]
        if advanced is None:
            advanced = rcParams["plotter"]["advanced"]
        if background_top_color is None:
            background_top_color = rcParams["plotter"]["background_top_color"]
        if background_bottom_color is None:
            background_bottom_color = \
                rcParams["plotter"]["background_bottom_color"]
        self.window_size = window_size
        if testing:
            # On Azure, AA and smoothing cause segfaults (access violation)
            self.advanced = False
        else:
            self.advanced = advanced
        self.background_top_color = background_top_color
        self.background_bottom_color = background_bottom_color

        self.resize(*self.window_size)
        self.set_background(
            color=self.background_bottom_color,
            top=self.background_top_color,
        )

        # configuration
        self.load_graphic_quality()

    def load_graphic_quality(self):
        """Configure the visual quality."""
        if self.advanced:
            self.set_anti_aliasing(True)
            self.set_line_smoothing(True)
            self.set_polygon_smoothing(True)
        else:
            self.set_anti_aliasing(False)
            self.set_line_smoothing(False)
            self.set_polygon_smoothing(False)
