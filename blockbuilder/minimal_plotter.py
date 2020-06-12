"""Module about minimal requirements for plotting."""

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from qtpy.QtWidgets import QMainWindow


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
        self.render_widget.Start()

    def closeEvent(self, event):
        """Clear the context properly."""
        self.render_widget.Finalize()
        event.accept()
