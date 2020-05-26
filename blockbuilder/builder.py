"""Module about the main application."""

import os.path as op
import enum
from functools import partial
import numpy as np
import vtk

from .params import rcParams
from .graphics import Graphics
from .elements import Element, Symmetry, SymmetrySelector, Grid, Plane, Block


@enum.unique
class BlockMode(enum.Enum):
    """List the modes available in Builder."""

    BUILD = enum.auto()
    DELETE = enum.auto()
    CAMERA = enum.auto()
    LIBRARY = enum.auto()
    SETTINGS = enum.auto()
    HELP = enum.auto()


@enum.unique
class Action(enum.Enum):
    """List the actions available in Builder."""

    RESET = enum.auto()


@enum.unique
class Toggle(enum.Enum):
    """List the toggles available in Builder."""

    SELECT = enum.auto()


class Builder(object):
    """Main application."""

    def __init__(self, dimensions=None):
        """Initialize the Builder."""
        self.unit = rcParams["unit"]
        self.azimuth = rcParams["builder"]["azimuth"]
        self.azimuth_rng = rcParams["builder"]["azimuth_rng"]
        self.elevation_rng = rcParams["builder"]["elevation_rng"]
        self.elevation = rcParams["builder"]["elevation"]
        if dimensions is None:
            dimensions = rcParams["builder"]["dimensions"]
        self.dimensions = np.asarray(dimensions)
        self.button_pressed = False
        self.floor = 0.
        self.ceiling = (self.dimensions[2] - 2) * self.unit
        self.icons = None
        self.graphics = None
        self.plotter = None
        self.toolbar = None
        self.picker = None
        self.current_block_mode = None
        self.mode_functions = None
        self.cached_coords = [-1, -1, -1]
        self.distance = np.max(self.dimensions) * 2 * self.unit
        self.distance_rng = [4 * self.unit, 2 * self.distance]

        # configuration
        self.load_elements()

        # XXX: experiment
        self.area_selection = False
        self.area_first_coords = None
        self.area_last_coords = None
        self.current_coords = None

        self.load_block_modes()
        self.load_interaction()
        self.load_icons()
        self.load_toolbar()

        # set initial frame
        self.plotter.reset_camera()
        self.update_camera()
        self.graphics.render()

    def update_camera(self):
        """Update the internal camera."""
        rad_azimuth = _deg2rad(self.azimuth)
        rad_elevation = _deg2rad(self.elevation)

        position = self.grid.center + [
            self.distance * np.cos(rad_azimuth) * np.sin(rad_elevation),
            self.distance * np.sin(rad_azimuth) * np.sin(rad_elevation),
            self.distance * np.cos(rad_elevation)]
        self.plotter.camera.SetViewUp((0., 0., 1.))
        self.plotter.camera.SetPosition(position)
        self.plotter.camera.SetFocalPoint(self.grid.center)

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

        # update pick
        x, y = self.plotter.interactor.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)
        self.graphics.render()

    def on_mouse_move(self, vtk_picker, event):
        """Process mouse move events."""
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)

    def on_mouse_wheel_forward(self, vtk_picker, event):
        """Process mouse wheel forward events."""
        tr = np.array([0., 0., self.unit])
        if self.grid.origin[2] < self.ceiling:
            self.grid.translate(tr)
            position = np.array(self.plotter.camera.GetPosition())
            self.plotter.camera.SetPosition(position + tr)
            self.plotter.camera.SetFocalPoint(self.grid.center)
        self.graphics.render()

    def on_mouse_wheel_backward(self, vtk_picker, event):
        """Process mouse wheel backward events."""
        tr = np.array([0., 0., -self.unit])
        if self.grid.origin[2] > self.floor:
            self.grid.translate(tr)
            position = np.array(self.plotter.camera.GetPosition())
            self.plotter.camera.SetPosition(position + tr)
            self.plotter.camera.SetFocalPoint(self.grid.center)
        self.graphics.render()

    def on_mouse_left_press(self, vtk_picker, event):
        """Process mouse left button press events."""
        self.button_pressed = True

    def on_mouse_left_release(self, vtk_picker, event):
        """Process mouse left button release events."""
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)
        self.button_pressed = False
        if self.area_selection:
            self.area_first_coords = None
            self.area_last_coords = None
            for area in self.selector.selection_area():
                self.operation(area)
            self.selector.reset_area()
        self.graphics.render()

    def on_pick(self, vtk_picker, event):
        """Process pick events."""
        func = self.mode_functions.get(self.current_block_mode, None)
        if func is not None:
            func(vtk_picker)

    def on_key_press(self, vtk_picker, event):
        key = self.plotter.interactor.GetKeySym()
        if key == 'Up':
            self.move_camera(update="distance", inverse=True)
        if key == 'Down':
            self.move_camera(update="distance")
        if key == 'q':
            self.move_camera(update="azimuth", inverse=True)
        if key == 'd':
            self.move_camera(update="azimuth")
        if key == 'z':
            self.move_camera(update="elevation", inverse=True)
        if key == 's':
            self.move_camera(update="elevation")

    def load_block_modes(self):
        """Load the block modes."""
        self.set_block_mode(BlockMode.BUILD)
        self.mode_functions = dict()
        for mode in BlockMode:
            func_name = "use_{}_mode".format(mode.name.lower())
            if hasattr(self, func_name):
                self.mode_functions[mode] = getattr(self, func_name)

    def load_elements(self):
        """Process the elements of the scene."""
        self.graphics = Graphics()
        self.plotter = self.graphics.plotter
        self.block = Block(self.plotter, self.dimensions)
        self.grid = Grid(self.plotter, self.dimensions)
        self.plane = Plane(self.plotter, self.dimensions)
        self.selector = SymmetrySelector(self.plotter, self.dimensions)
        self.selector.hide()

    def load_interaction(self):
        """Load interactions."""
        # allow flexible interactions
        style = vtk.vtkInteractorStyleUser()
        self.plotter.set_style(style)

        # enable cell picking
        self.picker = vtk.vtkCellPicker()
        self.picker.AddObserver(
            vtk.vtkCommand.EndPickEvent,
            self.on_pick
        )

        # setup the key bindings
        self.plotter.interactor.AddObserver(
            vtk.vtkCommand.MouseMoveEvent,
            self.on_mouse_move
        )
        self.plotter.interactor.AddObserver(
            vtk.vtkCommand.MouseWheelForwardEvent,
            self.on_mouse_wheel_forward
        )
        self.plotter.interactor.AddObserver(
            vtk.vtkCommand.MouseWheelBackwardEvent,
            self.on_mouse_wheel_backward
        )
        self.plotter.interactor.AddObserver(
            vtk.vtkCommand.LeftButtonPressEvent,
            self.on_mouse_left_press
        )
        self.plotter.interactor.AddObserver(
            vtk.vtkCommand.LeftButtonReleaseEvent,
            self.on_mouse_left_release
        )
        self.plotter.interactor.AddObserver(
            vtk.vtkCommand.KeyPressEvent,
            self.on_key_press
        )

    def load_icons(self):
        """Load the icons."""
        from PyQt5.Qt import QIcon
        self.icons = dict()
        for category in (BlockMode, Action, Toggle, Symmetry):
            for element in category:
                icon_path = "icons/{}.svg".format(element.name.lower())
                if op.isfile(icon_path):
                    self.icons[element] = QIcon(icon_path)

    def _add_toolbar_group(self, group, func, default_value):
        from PyQt5.QtWidgets import QToolButton, QButtonGroup
        button_group = QButtonGroup(parent=self.toolbar)
        for element in group:
            icon = self.icons.get(element, None)
            if icon is not None:
                button = QToolButton()
                button.setIcon(icon)
                button.setCheckable(True)
                if default_value is not None and element is default_value:
                    button.setChecked(True)
                button.toggled.connect(
                    partial(func, value=element))
                button_group.addButton(button)
                self.toolbar.addWidget(button)

    def _add_toolbar_actions(self):
        from PyQt5.QtWidgets import QToolButton
        for action in Action:
            icon = self.icons.get(action, None)
            if icon is not None:
                button = QToolButton()
                button.setIcon(icon)
                func_name = "action_{}".format(action.name.lower())
                func = getattr(self, func_name, None)
                if func is not None:
                    button.clicked.connect(func)
                self.toolbar.addWidget(button)

    def _add_toolbar_toggles(self):
        from PyQt5.QtWidgets import QToolButton
        for toggle in Toggle:
            icon = self.icons.get(toggle, None)
            if icon is not None:
                button = QToolButton()
                button.setIcon(icon)
                button.setCheckable(True)
                func_name = "toggle_{}".format(toggle.name.lower())
                func = getattr(self, func_name, None)
                if func is not None:
                    button.toggled.connect(func)
                self.toolbar.addWidget(button)

    def load_toolbar(self):
        """Initialize the toolbar."""
        self.toolbar = self.graphics.window.addToolBar("toolbar")
        self._add_toolbar_group(
            group=BlockMode,
            func=self.set_block_mode,
            default_value=BlockMode.BUILD,
        )
        self.toolbar.addSeparator()
        self._add_toolbar_toggles()
        self.toolbar.addSeparator()
        self._add_toolbar_group(
            group=Symmetry,
            func=self.selector.set_symmetry,
            default_value=Symmetry.SYMMETRY_NONE,
        )
        self.toolbar.addSeparator()
        self._add_toolbar_actions()

    def set_block_mode(self, value):
        """Set the current block mode."""
        if value in BlockMode:
            self.current_block_mode = value
            if self.grid is not None:
                self.grid.set_block_mode(value)
            if self.selector is not None:
                self.selector.set_block_mode(value)
        self.graphics.render()

    def use_delete_mode(self, vtk_picker):
        """Use the delete mode."""
        self._build_or_delete(vtk_picker, self.block.remove)

    def use_build_mode(self, vtk_picker):
        """Use the build mode."""
        self._build_or_delete(vtk_picker, self.block.add)

    def _build_or_delete(self, vtk_picker, operation):
        intersection = Intersection(vtk_picker)
        if not intersection.exist():
            self.selector.hide()
            self.graphics.render()
            return

        if not intersection.element(Element.GRID):
            return

        grid_ipoint = intersection.point(Element.GRID)

        coords = np.floor(grid_ipoint / self.unit)
        coords[2] = self.grid.origin[2] / self.unit
        self.coords = coords

        self.selector.select(coords)
        self.selector.show()

        if self.button_pressed:
            if self.area_selection:
                self.operation = operation
                if self.area_first_coords is None:
                    self.area_first_coords = self.coords
                else:
                    self.area_last_coords = self.coords
                    area = (self.area_first_coords, self.area_last_coords)
                    self.selector.select_area(area)
            else:
                for coords in self.selector.selection():
                    operation(coords)
                self.button_released = False
        self.graphics.render()

    def action_reset(self, unused):
        """Reset the block properties."""
        del unused
        self.block.remove_all()
        self.graphics.render()

    def toggle_select(self, value):
        """Toggle area selection."""
        self.area_selection = value


class Intersection(object):
    """Manage the intersections."""

    def __init__(self, picker):
        """Initialize the Intersection manager."""
        self.any_intersection = (picker.GetCellId() != -1)
        if self.any_intersection:
            self.intersections = [None for element in Element]
            self.picked_points = picker.GetPickedPositions()
            self.picked_actors = picker.GetActors()
            for idx, actor in enumerate(self.picked_actors):
                self.intersections[actor.element_id.value] = idx

    def exist(self):
        """Return True is there is any intersection."""
        return self.any_intersection

    def element(self, element_id):
        """Return True is there is any intersection with element_id."""
        return self.intersections[element_id.value] is not None

    def point(self, element_id):
        """Return the intersection point of element_id."""
        idx = self.intersections[element_id.value]
        return np.asarray(self.picked_points.GetPoint(idx))


def _clamp(value, rng):
    value = rng[1] if value > rng[1] else value
    value = rng[0] if value < rng[0] else value
    return value


def _deg2rad(deg):
    return deg * np.pi / 180.


def _rad2deg(rad):
    return rad * 180. / np.pi
