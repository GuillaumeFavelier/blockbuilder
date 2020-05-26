"""Module about visual properties."""

from vtk import vtkRenderer, vtkDataSetMapper, vtkActor
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow
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
        import scooby
        if scooby.in_ipython():  # pragma: no cover
            from IPython import get_ipython
            ipython = get_ipython()
            ipython.magic('gui qt')
            from IPython.external.qt_for_kernel import QtGui
            QtGui.QApplication.instance()

        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:  # pragma: no cover
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
        self.main_window = None
        self.render_widget = None
        self.render_window = None
        self.renderer = None
        self.interactor = None
        self.app = None


class Plotter(MinimalPlotter):
    """."""
    def __init__(self, window_size):
        super().__init__()
        self.resize(window_size)

    def resize(self, window_size):
        """Resize the window."""
        self.main_window.resize(*window_size)

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

    def set_line_smoothing(self, value):
        """Enable/Disable line smoothing."""
        self.render_window.SetLineSmoothing(value)

    def set_polygon_smoothing(self, value):
        """Enable/Disable line smoothing."""
        self.render_window.SetPolygonSmoothing(value)

    def set_style(self, style):
        """Set the interactor style."""
        self.interactor.SetInteractorStyle(style)

    def reset_camera(self):
        """Reset the camera."""
        self.renderer.ResetCamera()

    def add_mesh(self, mesh, **kwargs):
        mapper = vtkDataSetMapper()
        mapper.SetInputData(mesh)
        actor = vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
        return actor


class Graphics(object):
    """Manage the visual properties."""

    def __init__(self, window_size=None, line_width=None, advanced=None,
                 background_top_color=None,
                 background_bottom_color=None):
        """Initialize the default visual properties."""
        if window_size is None:
            window_size = rcParams["graphics"]["window_size"]
        if line_width is None:
            line_width = rcParams["graphics"]["line_width"]
        if advanced is None:
            advanced = rcParams["graphics"]["advanced"]
        if background_top_color is None:
            background_top_color = rcParams["graphics"]["background_top_color"]
        if background_bottom_color is None:
            background_bottom_color = \
                rcParams["graphics"]["background_bottom_color"]
        self.window_size = window_size
        self.line_width = line_width
        self.advanced = advanced
        self.background_top_color = background_top_color
        self.background_bottom_color = background_bottom_color
        self.plotter = None
        self.window = None

        # configuration
        self.load_plotter()
        self.load_graphic_quality()

    def render(self):
        """Render the scene."""
        # fix the clipping planes being too small
        rng = [0] * 6
        self.plotter.renderer.ComputeVisiblePropBounds(rng)
        self.plotter.renderer.ResetCameraClippingRange(rng)
        if hasattr(self.plotter, "render_window"):
            self.plotter.render_window.Render()

    def load_plotter(self):
        """Configure the internal plotter."""
        self.plotter = Plotter(window_size=self.window_size)
        self.window = self.plotter.main_window
        self.plotter.set_background(
            color=self.background_bottom_color,
            top=self.background_top_color,
        )
        self.plotter.show()
        # XXX: Enable axes
        # self.plotter.show_axes()

    def load_graphic_quality(self):
        """Configure the visual quality."""
        if self.advanced:
            self.plotter.set_anti_aliasing(True)
            self.plotter.set_line_smoothing(True)
            self.plotter.set_polygon_smoothing(True)
        else:
            self.plotter.set_anti_aliasing(False)
            self.plotter.set_line_smoothing(False)
            self.plotter.set_polygon_smoothing(False)
