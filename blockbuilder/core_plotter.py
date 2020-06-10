"""Module about core visual properties."""

import vtk
from .minimal_plotter import MinimalPlotter


class CorePlotter(MinimalPlotter):
    """Plotter specialized in low-level operations."""

    def __init__(self, params, parent=None, window_size=None,
                 advanced=None, background_top_color=None,
                 background_bottom_color=None, testing=False):
        """Initialize the CorePlotter."""
        super().__init__(parent=parent)
        self.params = params
        self.show_edges = self.params["plotter"]["show_edges"]
        self.line_width = self.params["plotter"]["line_width"]
        if window_size is None:
            window_size = self.params["plotter"]["window_size"]
        if advanced is None:
            advanced = self.params["plotter"]["advanced"]
        if background_top_color is None:
            background_top_color = \
                self.params["plotter"]["background"]["color"]["top"]
        if background_bottom_color is None:
            background_bottom_color = \
                self.params["plotter"]["background"]["color"]["bottom"]
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
        self.renderer.Modified()
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
