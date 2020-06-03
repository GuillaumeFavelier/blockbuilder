import numpy as np
import vtk
from .params import rcParams
from .plotter import Plotter


class InteractivePlotter(Plotter):

    def __init__(self, parent=None, testing=False):
        super().__init__(parent=parent, testing=testing)
        self.azimuth = rcParams["builder"]["azimuth"]
        self.azimuth_rng = rcParams["builder"]["azimuth_rng"]
        self.elevation_rng = rcParams["builder"]["elevation_rng"]
        self.elevation = rcParams["builder"]["elevation"]
        self.view_up = rcParams["builder"]["view_up"]
        self.focal_point = np.array([0, 0, 0])
        self.picker = None

        # configure
        self.load_interaction()

    def move_camera(self, update, inverse=False):
        """Move the camera depending on the given update property."""
        if inverse:
            delta = -2
        else:
            delta = 2
        if update == "azimuth":
            self.azimuth += delta
            if self.azimuth < self.azimuth_rng[0]:
                self.azimuth = self.azimuth + self.azimuth_rng[1]
            if self.azimuth > self.azimuth_rng[1]:
                self.azimuth = self.azimuth % self.azimuth_rng[1]
        elif update == "elevation":
            self.elevation += delta
            self.elevation = _clamp(self.elevation, self.elevation_rng)
        elif update == "distance":
            self.distance += delta
            self.distance = _clamp(self.distance, self.distance_rng)
        self.update_camera()

    def update_camera(self):
        """Update the internal camera."""
        rad_azimuth = _deg2rad(self.azimuth)
        rad_elevation = _deg2rad(self.elevation)
        position = self.focal_point + [
            self.distance * np.cos(rad_azimuth) * np.sin(rad_elevation),
            self.distance * np.sin(rad_azimuth) * np.sin(rad_elevation),
            self.distance * np.cos(rad_elevation)]
        self.camera.SetViewUp(self.view_up)
        self.camera.SetPosition(position)
        self.camera.SetFocalPoint(self.focal_point)

    def on_key_press(self, vtk_picker, event):
        """Process key press events."""
        key = self.interactor.GetKeySym()
        if key == rcParams["builder"]["bindings"]["distance_minus"]:
            self.move_camera(update="distance", inverse=True)
        if key == rcParams["builder"]["bindings"]["distance_plus"]:
            self.move_camera(update="distance")
        if key == rcParams["builder"]["bindings"]["azimuth_minus"]:
            self.move_camera(update="azimuth", inverse=True)
        if key == rcParams["builder"]["bindings"]["azimuth_plus"]:
            self.move_camera(update="azimuth")
        if key == rcParams["builder"]["bindings"]["elevation_minus"]:
            self.move_camera(update="elevation", inverse=True)
        if key == rcParams["builder"]["bindings"]["elevation_plus"]:
            self.move_camera(update="elevation")

    def load_interaction(self):
        """Load interactions."""
        # disable default interactions
        self.set_style(None)

        # enable cell picking
        if hasattr(self, "on_pick") and\
           callable(self.on_pick):
            self.picker = vtk.vtkCellPicker()
            self.picker.AddObserver(
                vtk.vtkCommand.EndPickEvent,
                self.on_pick
            )

        # setup the observers
        if hasattr(self, "on_mouse_move") and \
           callable(self.on_mouse_move):
            self.interactor.AddObserver(
                vtk.vtkCommand.MouseMoveEvent,
                self.on_mouse_move
            )
        if hasattr(self, "on_mouse_wheel_forward") and\
           callable(self.on_mouse_wheel_forward):
            self.interactor.AddObserver(
                vtk.vtkCommand.MouseWheelForwardEvent,
                self.on_mouse_wheel_forward
            )
        if hasattr(self, "on_mouse_wheel_backward") and\
           callable(self.on_mouse_wheel_backward):
            self.interactor.AddObserver(
                vtk.vtkCommand.MouseWheelBackwardEvent,
                self.on_mouse_wheel_backward
            )
        if hasattr(self, "on_mouse_left_press") and\
           callable(self.on_mouse_left_press):
            self.interactor.AddObserver(
                vtk.vtkCommand.LeftButtonPressEvent,
                self.on_mouse_left_press
            )
        if hasattr(self, "on_mouse_left_release") and\
           callable(self.on_mouse_left_release):
            self.interactor.AddObserver(
                vtk.vtkCommand.LeftButtonReleaseEvent,
                self.on_mouse_left_release
            )
        if hasattr(self, "on_key_press") and\
           callable(self.on_key_press):
            self.interactor.AddObserver(
                vtk.vtkCommand.KeyPressEvent,
                self.on_key_press
            )


def _deg2rad(deg):
    return deg * np.pi / 180.


def _rad2deg(rad):
    return rad * 180. / np.pi


def _clamp(value, rng):
    value = rng[1] if value > rng[1] else value
    value = rng[0] if value < rng[0] else value
    return value