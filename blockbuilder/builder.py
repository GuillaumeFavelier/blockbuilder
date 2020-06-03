"""Module about the main application."""

import enum
from functools import partial
import numpy as np
import vtk

from .params import rcParams
from .plotter import Plotter
from .elements import Element, Symmetry, SymmetrySelector, Grid, Plane, Block
from .intersection import Intersection

from PyQt5 import QtCore
from PyQt5.Qt import QIcon, QSize
from PyQt5.QtWidgets import (QPushButton, QToolButton, QButtonGroup,
                             QColorDialog, QFileDialog)


@enum.unique
class BlockMode(enum.Enum):
    """List the modes available in Builder."""

    BUILD = enum.auto()
    DELETE = enum.auto()
    # CAMERA = enum.auto()
    # LIBRARY = enum.auto()
    # SETTINGS = enum.auto()
    # HELP = enum.auto()


@enum.unique
class Action(enum.Enum):
    """List the actions available in Builder."""

    RESET = enum.auto()
    IMPORT = enum.auto()
    EXPORT = enum.auto()


@enum.unique
class Toggle(enum.Enum):
    """List the toggles available in Builder."""

    SELECT = enum.auto()
    EDGES = enum.auto()


class Builder(Plotter):
    """Main application."""

    def __init__(self, parent=None, testing=False):
        """Initialize the Builder."""
        super().__init__(parent=parent, testing=testing)
        self.unit = rcParams["unit"]
        self.default_block_color = rcParams["block"]["color"]
        self.azimuth = rcParams["builder"]["azimuth"]
        self.azimuth_rng = rcParams["builder"]["azimuth_rng"]
        self.elevation_rng = rcParams["builder"]["elevation_rng"]
        self.elevation = rcParams["builder"]["elevation"]
        self.toolbar_area = rcParams["app"]["toolbar"]["area"]
        self.icon_size = rcParams["app"]["toolbar"]["icon_size"]
        self.dimensions = rcParams["builder"]["dimensions"]
        self.set_dimensions(self.dimensions)
        self.button_pressed = False
        self.button_released = False
        self.area_selection = False
        self.floor = 0.
        self.icons = None
        self.toolbar = None
        self.picker = None
        self.current_block_mode = None
        self.mode_functions = None
        self.cached_coords = [-1, -1, -1]

        # configuration
        self.show()
        self.load_elements()
        self.add_elements()
        self.load_block_modes()
        self.load_interaction()
        self.load_icons()
        self.load_toolbar()
        self.selector.hide()
        self.update_camera()
        self.render_scene()

    def update_camera(self):
        """Update the internal camera."""
        rad_azimuth = _deg2rad(self.azimuth)
        rad_elevation = _deg2rad(self.elevation)

        position = self.grid.center + [
            self.distance * np.cos(rad_azimuth) * np.sin(rad_elevation),
            self.distance * np.sin(rad_azimuth) * np.sin(rad_elevation),
            self.distance * np.cos(rad_elevation)]
        self.camera.SetViewUp((0., 0., 1.))
        self.camera.SetPosition(position)
        self.camera.SetFocalPoint(self.grid.center)

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
        x, y = self.interactor.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)
        self.render_scene()

    def on_mouse_move(self, vtk_picker, event):
        """Process mouse move events."""
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)

    def on_mouse_wheel_forward(self, vtk_picker, event):
        """Process mouse wheel forward events."""
        tr = np.array([0., 0., self.unit])
        if self.grid.origin[2] < self.ceiling:
            self.grid.translate(tr)
            position = np.array(self.camera.GetPosition())
            self.camera.SetPosition(position + tr)
            self.camera.SetFocalPoint(self.grid.center)
        self.render_scene()

    def on_mouse_wheel_backward(self, vtk_picker, event):
        """Process mouse wheel backward events."""
        tr = np.array([0., 0., -self.unit])
        if self.grid.origin[2] > self.floor:
            self.grid.translate(tr)
            position = np.array(self.camera.GetPosition())
            self.camera.SetPosition(position + tr)
            self.camera.SetFocalPoint(self.grid.center)
        self.render_scene()

    def on_mouse_left_press(self, vtk_picker, event):
        """Process mouse left button press events."""
        x, y = vtk_picker.GetEventPosition()
        self.button_pressed = True
        self.picker.Pick(x, y, 0, self.renderer)

    def on_mouse_left_release(self, vtk_picker, event):
        """Process mouse left button release events."""
        x, y = vtk_picker.GetEventPosition()
        self.button_released = True
        self.picker.Pick(x, y, 0, self.renderer)
        self.button_pressed = False

    def on_pick(self, vtk_picker, event):
        """Process pick events."""
        func = self.mode_functions.get(self.current_block_mode, None)
        if func is not None:
            func(vtk_picker)

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

    def load_block_modes(self):
        """Load the block modes."""
        self.set_block_mode(BlockMode.BUILD)
        self.mode_functions = dict()
        for mode in BlockMode:
            func_name = "use_{}_mode".format(mode.name.lower())
            if hasattr(self, func_name):
                self.mode_functions[mode] = getattr(self, func_name)

    def add_element(self, element):
        """Add an element to the scene."""
        actor = self.add_mesh(**element.plotting)
        element.actor = actor
        actor.element_id = element.element_id

    def add_elements(self):
        """Add all the default elements to the scene."""
        self.add_element(self.block)
        self.add_element(self.grid)
        self.add_element(self.plane)
        self.add_element(self.selector)
        self.add_element(self.selector.selector_x)
        self.add_element(self.selector.selector_y)
        self.add_element(self.selector.selector_xy)

    def remove_elements(self):
        """Remove all the default elements of the scene."""
        self.renderer.RemoveActor(self.block.actor)
        self.renderer.RemoveActor(self.grid.actor)
        self.renderer.RemoveActor(self.plane.actor)
        self.renderer.RemoveActor(self.selector.actor)
        self.renderer.RemoveActor(self.selector.selector_x.actor)
        self.renderer.RemoveActor(self.selector.selector_y.actor)
        self.renderer.RemoveActor(self.selector.selector_xy.actor)

    def load_elements(self):
        """Load the default elements."""
        self.block = Block(self.dimensions)
        self.grid = Grid(self.dimensions)
        self.plane = Plane(self.dimensions)
        self.selector = SymmetrySelector(self.dimensions)

    def load_interaction(self):
        """Load interactions."""
        # disable default interactions
        self.set_style(None)

        # enable cell picking
        self.picker = vtk.vtkCellPicker()
        self.picker.AddObserver(
            vtk.vtkCommand.EndPickEvent,
            self.on_pick
        )

        # setup the key bindings
        self.interactor.AddObserver(
            vtk.vtkCommand.MouseMoveEvent,
            self.on_mouse_move
        )
        self.interactor.AddObserver(
            vtk.vtkCommand.MouseWheelForwardEvent,
            self.on_mouse_wheel_forward
        )
        self.interactor.AddObserver(
            vtk.vtkCommand.MouseWheelBackwardEvent,
            self.on_mouse_wheel_backward
        )
        self.interactor.AddObserver(
            vtk.vtkCommand.LeftButtonPressEvent,
            self.on_mouse_left_press
        )
        self.interactor.AddObserver(
            vtk.vtkCommand.LeftButtonReleaseEvent,
            self.on_mouse_left_release
        )
        self.interactor.AddObserver(
            vtk.vtkCommand.KeyPressEvent,
            self.on_key_press
        )

    def load_icons(self):
        """Load the icons.

        The resource configuration file ``blockbuilder/icons/blockbuilder.qrc``
        describes the location of the resources in the filesystem and
        also defines aliases for their use in the code.

        To automatically generate the resource file in ``blockbuilder/icons``:
        pyrcc5 -o blockbuilder/icons/resources.py blockbuilder/icons/mne.qrc
        """
        from .icons import resources
        resources.qInitResources()
        self.icons = dict()
        for category in (BlockMode, Action, Toggle, Symmetry):
            for element in category:
                icon_resource = ":/{}.svg".format(element.name.lower())
                self.icons[element] = QIcon(icon_resource)

    def _add_toolbar_group(self, group, func, default_value):
        button_group = QButtonGroup(parent=self.toolbar)
        for element in group:
            icon = self.icons.get(element, None)
            if icon is not None:
                button = QToolButton()
                button.setFixedSize(QSize(*self.icon_size))
                button.setIcon(icon)
                button.setCheckable(True)
                if default_value is not None and element is default_value:
                    button.setChecked(True)
                button.toggled.connect(
                    partial(func, value=element))
                button_group.addButton(button)
                self.toolbar.addWidget(button)

    def _add_toolbar_actions(self):
        for action in Action:
            icon = self.icons.get(action, None)
            if icon is not None:
                button = QToolButton()
                button.setFixedSize(QSize(*self.icon_size))
                button.setIcon(icon)
                func_name = "action_{}".format(action.name.lower())
                func = getattr(self, func_name, None)
                if func is not None:
                    button.clicked.connect(func)
                self.toolbar.addWidget(button)

    def _add_toolbar_toggles(self):
        for toggle in Toggle:
            icon = self.icons.get(toggle, None)
            if icon is not None:
                button = QToolButton()
                button.setFixedSize(QSize(*self.icon_size))
                button.setIcon(icon)
                button.setCheckable(True)
                toggle_name = toggle.name.lower()
                func_name = "toggle_{}".format(toggle_name)
                func = getattr(self, func_name, None)
                if func is not None:
                    button.toggled.connect(func)
                button.setChecked(rcParams["builder"]["toggles"][toggle_name])
                self.toolbar.addWidget(button)

    def _add_toolbar_color_button(self):
        self.color_button = QPushButton()
        self.color_button.setFixedSize(QSize(*self.icon_size))
        self.color_button.clicked.connect(self.set_block_color)
        self.toolbar.addWidget(self.color_button)
        self.set_block_color(self.default_block_color, is_int=False)

    def load_toolbar(self):
        """Initialize the toolbar."""
        self.toolbar = self.addToolBar("toolbar")
        self.addToolBar(
            _get_toolbar_area(self.toolbar_area),
            self.toolbar,
        )
        self.toolbar.setIconSize(QSize(*self.icon_size))
        self._add_toolbar_color_button()
        self.toolbar.addSeparator()
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
            func=self.set_symmetry,
            default_value=Symmetry.SYMMETRY_NONE,
        )
        self.toolbar.addSeparator()
        self._add_toolbar_actions()

    def set_dimensions(self, dimensions):
        """Set the current dimensions."""
        self.dimensions = np.asarray(dimensions)
        self.ceiling = (self.dimensions[2] - 2) * self.unit
        self.distance = np.max(self.dimensions) * 2 * self.unit
        self.distance_rng = [4 * self.unit, 2 * self.distance]

    def set_symmetry(self, value):
        """Set the current symmetry."""
        self.selector.set_symmetry(value)

    def set_block_mode(self, value=None):
        """Set the current block mode."""
        if value is None:
            value = self.current_block_mode
        else:
            self.current_block_mode = value
        if value in BlockMode:
            if self.grid is not None:
                self.grid.set_block_mode(value)
            if self.selector is not None:
                self.selector.set_block_mode(value)
        self.render_scene()

    def set_block_color(self, value=None, is_int=True):
        """Set the current block color."""
        if isinstance(value, bool):
            color = QColorDialog.getColor()
            color = _qrgb2rgb(color)
        else:
            color = value
        color = np.asarray(color)
        self.color_button.setStyleSheet(
            "background-color: rgb" + _rgb2str(color, is_int))
        self.block.set_color(color, is_int)

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
            self.render_scene()
            return

        if not intersection.element(Element.GRID):
            return

        grid_ipoint = intersection.point(Element.GRID)

        coords = np.floor(grid_ipoint / self.unit)
        coords[2] = self.grid.origin[2] / self.unit
        self.coords = coords

        self.selector.select(coords)
        self.selector.show()

        if self.area_selection:
            if self.button_released:
                first_set = self.selector.get_first_coords() is not None
                last_set = self.selector.get_last_coords() is not None
                if first_set and last_set:
                    for area in self.selector.selection_area():
                        operation(area)
                elif first_set and not last_set:
                    for coords in self.selector.selection():
                        operation(coords)
                self.selector.reset_area()
                self.button_released = False
            elif self.button_pressed:
                if self.selector.get_first_coords() is None:
                    self.selector.set_first_coords(coords)
                else:
                    self.selector.set_last_coords(coords)
                    area = (
                        self.selector.get_first_coords(),
                        self.selector.get_last_coords(),
                    )
                    self.selector.select_area(area)
        else:
            if self.button_pressed:
                for coords in self.selector.selection():
                    operation(coords)

        self.render_scene()

    def action_reset(self, unused):
        """Reset the block properties."""
        del unused
        self.block.remove_all()
        self.set_block_color(self.default_block_color, is_int=False)
        self.render_scene()

    def action_import(self, unused):
        """Import an external blockset."""
        del unused
        filename = QFileDialog.getOpenFileName(
            None,
            "Import Blockset",
            filter="Blockset (*.vts *.vtk)",
        )
        filename = filename[0]
        if len(filename) > 0:
            reader = vtk.vtkXMLStructuredGridReader()
            reader.SetFileName(filename)
            reader.Update()
            mesh = reader.GetOutput()
            dimensions = mesh.GetDimensions()
            imported_block = Block(dimensions, mesh)
            if all(np.equal(dimensions, self.dimensions)):
                self.block.merge(imported_block)
            else:
                final_dimensions = [
                    self.block.dimensions,
                    imported_block.dimensions
                ]
                final_dimensions = np.max(final_dimensions, axis=0)

                if all(np.equal(self.dimensions, final_dimensions)):
                    self.block.merge(imported_block)
                else:
                    self.remove_elements()

                    old_block = self.block
                    self.set_dimensions(final_dimensions)
                    self.load_elements()
                    self.add_elements()
                    self.set_block_mode()
                    self.block.merge(old_block)
                    self.block.merge(imported_block)

                    self.selector.hide()
                    self.update_camera()
            self.render_scene()

    def action_export(self, unused):
        """Export the internal blockset."""
        filename = QFileDialog.getSaveFileName(
            None,
            "Export Blockset",
            "Untitled.vts",
            "Blockset (*.vts *.vtk)",
        )
        filename = filename[0]
        if len(filename) > 0:
            writer = vtk.vtkXMLStructuredGridWriter()
            writer.SetFileName(filename)
            writer.SetInputData(self.block.mesh)
            writer.Write()

    def toggle_select(self, value):
        """Toggle area selection."""
        self.area_selection = value

    def toggle_edges(self, value):
        """Toggle area selection."""
        self.block.toggle_edges(value)
        self.render_scene()


def _get_toolbar_area(area):
    if area == "left":
        return QtCore.Qt.LeftToolBarArea
    if area == "right":
        return QtCore.Qt.RightToolBarArea
    if area == "top":
        return QtCore.Qt.TopToolBarArea
    if area == "bottom":
        return QtCore.Qt.BottomToolBarArea


def _clamp(value, rng):
    value = rng[1] if value > rng[1] else value
    value = rng[0] if value < rng[0] else value
    return value


def _deg2rad(deg):
    return deg * np.pi / 180.


def _rad2deg(rad):
    return rad * 180. / np.pi


def _rgb2str(color, is_int=False):
    if not is_int:
        color = np.asarray(color) * 255
        color = color.astype(np.uint8)
    return str(tuple(color))


def _qrgb2rgb(color):
    return (
        color.red(),
        color.green(),
        color.blue()
    )
