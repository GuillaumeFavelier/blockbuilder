"""Module about visual properties."""

import scooby
from vtk import vtkRenderer, vtkDataSetMapper, vtkActor
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow
from .params import rcParams


class MainWindow(QMainWindow):
    """Simple window."""

    signal_close = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the main window."""
        super(MainWindow, self).__init__(parent)

    def closeEvent(self, event):
        """Manage the close event."""
        self.signal_close.emit()
        event.accept()


class MinimalPlotter(QObject):
    """Minimal plotter."""

    def __init__(self):
        """Initialize the MinimalPlotter."""
        super().__init__()
        if scooby.in_ipython():
            from IPython import get_ipython
            ipython = get_ipython()
            ipython.magic('gui qt')
            from IPython.external.qt_for_kernel import QtGui
            QtGui.QApplication.instance()
        app = QApplication.instance()
        if not app:
            app = QApplication([''])
        self.app = app

        self.main_window = MainWindow()
        self.main_window.signal_close.connect(self._delete)
        self.render_widget = QVTKRenderWindowInteractor()
        self.render_widget.Initialize()
        self.render_widget.Start()
        self.renderer = vtkRenderer()
        self.camera = self.renderer.GetActiveCamera()
        self.render_window = self.render_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = self.render_window.GetInteractor()
        self.main_window.setCentralWidget(self.render_widget)

    def show(self):
        """Show the plotter."""
        self.main_window.show()

    def _delete(self):
        """Decrease reference count to avoid cycle."""
        # XXX: Why main_window refcount cannot decrease?
        # self.main_window = None
        self.render_widget = None
        self.render_window = None
        self.renderer = None
        self.interactor = None
        self.app = None


class CorePlotter(MinimalPlotter):
    """Plotter specialized in low-level operations."""

    def __init__(self):
        """Initialize the Plotter."""
        super().__init__()

    def resize(self, window_size):
        """Resize the window."""
        self.main_window.resize(*window_size)
        self.window_size = window_size

    def set_background(self, color, top=None):
        """Set the background color."""
        self.renderer.SetBackground(color)
        if top is None:
            self.renderer.GradientBackgroundOff()
        else:
            self.renderer.GradientBackgroundOn()
            self.renderer.SetBackground2(top)

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

    def reset_camera(self):
        """Reset the camera."""
        self.renderer.ResetCamera()

    def render(self):
        """Render the scene."""
        # fix the clipping planes being too small
        rng = [0] * 6
        self.renderer.ComputeVisiblePropBounds(rng)
        self.renderer.ResetCameraClippingRange(rng)
        self.render_window.Render()

    def add_mesh(self, mesh, **kwargs):
        """Add a mesh to the scene."""
        mapper = vtkDataSetMapper()
        mapper.SetInputData(mesh)
        actor = vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
        return actor


class Plotter(CorePlotter):
    """Main plotter."""

    def __init__(self, window_size=None, line_width=None, advanced=None,
                 background_top_color=None,
                 background_bottom_color=None):
        """Initialize the default visual properties."""
        super().__init__()
        if window_size is None:
            window_size = rcParams["plotter"]["window_size"]
        if line_width is None:
            line_width = rcParams["plotter"]["line_width"]
        if advanced is None:
            advanced = rcParams["plotter"]["advanced"]
        if background_top_color is None:
            background_top_color = rcParams["plotter"]["background_top_color"]
        if background_bottom_color is None:
            background_bottom_color = \
                rcParams["plotter"]["background_bottom_color"]
        self.window_size = window_size
        self.line_width = line_width
        self.advanced = advanced
        self.background_top_color = background_top_color
        self.background_bottom_color = background_bottom_color

        self.resize(self.window_size)
        self.set_background(
            color=self.background_bottom_color,
            top=self.background_top_color,
        )
        self.show()

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
