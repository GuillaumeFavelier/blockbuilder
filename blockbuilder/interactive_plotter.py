"""Module about interactions with a plotter."""

import numpy as np
import vtk
from .core_plotter import CorePlotter


class InteractivePlotter(CorePlotter):
    """Plotter with interactions."""

    def __init__(self, params, parent=None, testing=False):
        """Initialize the InteractivePlotter."""
        super().__init__(params=params, parent=parent, testing=testing)
        self.azimuth = self.params["camera"]["azimuth"]
        self.azimuth_rng = self.params["camera"]["azimuth_rng"]
        self.elevation_rng = self.params["camera"]["elevation_rng"]
        self.elevation = self.params["camera"]["elevation"]
        self.view_up = self.params["camera"]["view_up"]
        self.focal_point = np.array([0, 0, 0])
        self.picker = None

        bounds = np.array(self.renderer.ComputeVisiblePropBounds())
        self.distance = max(bounds[1::2] - bounds[::2]) * 2.0
        self.distance_rng = [self.distance * 0.5, self.distance * 1.5]

        # configure
        self.load_interaction()

    def set_focal_point(self, point):
        """Set the focal point."""
        self.focal_point = point
        self.camera.SetFocalPoint(self.grid.center)

    def translate_camera(self, tr):
        """Translate the camera."""
        position = np.array(self.camera.GetPosition())
        self.camera.SetPosition(position + tr)

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
        else:
            raise ValueError("Expected value for ``update`` is ``azimuth``, "
                             "``elevation`` or ``distance`` but {} was given."
                             .format(update))
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
        if key == self.params["keybinding"]["distance_minus"]["value"]:
            self.move_camera(update="distance", inverse=True)
        if key == self.params["keybinding"]["distance_plus"]["value"]:
            self.move_camera(update="distance")
        if key == self.params["keybinding"]["azimuth_minus"]["value"]:
            self.move_camera(update="azimuth", inverse=True)
        if key == self.params["keybinding"]["azimuth_plus"]["value"]:
            self.move_camera(update="azimuth")
        if key == self.params["keybinding"]["elevation_minus"]["value"]:
            self.move_camera(update="elevation", inverse=True)
        if key == self.params["keybinding"]["elevation_plus"]["value"]:
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

        # setup key press observer
        self.interactor.AddObserver(
            vtk.vtkCommand.KeyPressEvent,
            self.on_key_press
        )
        # setup the other observers
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


def _deg2rad(deg):
    return deg * np.pi / 180.


def _clamp(value, rng):
    value = rng[1] if value > rng[1] else value
    value = rng[0] if value < rng[0] else value
    return value
