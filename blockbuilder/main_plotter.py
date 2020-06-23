"""Module about the main application."""

import enum
import numpy as np
import vtk

from qtpy import QtCore
from qtpy.QtCore import QSize
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (QToolButton, QButtonGroup,
                            QFileDialog)

from .utils import DefaultFunction
from .element import ElementId
from .selector import Symmetry, SymmetrySelector
from .grid import Grid
from .plane import Plane
from .block import Block
from .intersection import Intersection
from .interactive_plotter import InteractivePlotter
from .setting import SettingDialog, ColorButton
from .help import HelpDialog


@enum.unique
class BlockMode(enum.Enum):
    """List the modes available in MainPlotter."""

    BUILD = enum.auto()
    DELETE = enum.auto()


@enum.unique
class Action(enum.Enum):
    """List the actions available in MainPlotter."""

    RESET = enum.auto()
    IMPORT = enum.auto()
    EXPORT = enum.auto()
    SETTING = enum.auto()
    HELP = enum.auto()


@enum.unique
class Toggle(enum.Enum):
    """List the toggles available in MainPlotter."""

    AREA = enum.auto()
    EDGES = enum.auto()


class MainPlotter(InteractivePlotter):
    """Main application."""

    def __init__(self, params, parent=None, testing=False):
        """Initialize the MainPlotter."""
        super().__init__(params, parent=parent, testing=testing)
        self.unit = self.params["unit"]
        self.dimensions = self.params["dimensions"]
        self.default_block_color = self.params["block"]["color"]
        self.icon_size = self.params["builder"]["toolbar"]["icon_size"]
        self.button_pressed = False
        self.button_released = False
        self.area_selection = False
        self.floor = None
        self.ceiling = None
        self.icons = None
        self.toolbar = None
        self.current_block_mode = None
        self.mode_functions = None
        self.set_dimensions(self.dimensions)

        # configuration
        self.show()
        self.load_elements()
        self.add_elements()
        self.load_block_modes()
        self.load_icons()
        self.load_toolbar()
        self.load_dialogs()
        self.selector.hide()
        self.update_camera()
        self.render_scene()

    def update_camera(self):
        """Update the internal camera."""
        self.set_focal_point(self.grid.center)
        super().update_camera()

    def move_camera(self, update, inverse=False):
        """Trigger a pick when moving the camera."""
        super().move_camera(update, inverse)
        x, y = self.interactor.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)
        self.render_scene()

    def translate_camera(self, tr):
        """Translate the camera."""
        self.grid.translate(tr)
        self.set_focal_point(self.grid.center)
        super().translate_camera(tr)

    def on_mouse_move(self, vtk_picker, event):
        """Process mouse move events."""
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)

    def on_mouse_wheel_forward(self, vtk_picker, event):
        """Process mouse wheel forward events."""
        tr = np.array([0., 0., self.unit])
        if self.grid.origin[2] < self.ceiling:
            self.translate_camera(tr)
        self.render_scene()

    def on_mouse_wheel_backward(self, vtk_picker, event):
        """Process mouse wheel backward events."""
        tr = np.array([0., 0., -self.unit])
        if self.grid.origin[2] > self.floor:
            self.translate_camera(tr)
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
        func(vtk_picker)

    def load_block_modes(self):
        """Load the block modes."""
        self.set_block_mode(BlockMode.BUILD)
        self.mode_functions = dict()
        for mode in BlockMode:
            func_name = "use_{}_mode".format(mode.name.lower())
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

    def remove_element(self, element):
        """Remove an elements from the scene."""
        self.renderer.RemoveActor(element.actor)
        element.actor = None

    def remove_elements(self):
        """Remove all the default elements of the scene."""
        self.remove_element(self.block)
        self.remove_element(self.grid)
        self.remove_element(self.plane)
        self.remove_element(self.selector)
        self.remove_element(self.selector.selector_x)
        self.remove_element(self.selector.selector_y)
        self.remove_element(self.selector.selector_xy)

    def load_elements(self):
        """Load the default elements."""
        self.block = Block(self.params, self.dimensions)
        self.grid = Grid(self.params, self.dimensions)
        self.plane = Plane(self.params, self.dimensions)
        self.selector = SymmetrySelector(self.params, self.dimensions)

    def load_icons(self):
        """Load the icons.

        The resource configuration file ``blockbuilder/icons/blockbuilder.qrc``
        describes the location of the resources in the filesystem and
        also defines aliases for their use in the code.

        To automatically generate the resource file in ``blockbuilder/icons``:
        pyrcc5 -o resources.py blockbuilder.qrc
        """
        self.icons = dict()
        for category in (BlockMode, Toggle, Symmetry, Action):
            for element in category:
                icon_resource = ":/{}.svg".format(element.name.lower())
                self.icons[element] = QIcon(icon_resource)

    def _add_toolbar_group(self, group, func, default_value):
        button_group = QButtonGroup(parent=self.toolbar)
        for element in group:
            icon = self.icons.get(element, None)
            button = QToolButton()
            button.setFixedSize(QSize(*self.icon_size))
            button.setIcon(icon)
            button.setCheckable(True)
            if default_value is not None and element is default_value:
                button.setChecked(True)
            button.toggled.connect(DefaultFunction(func, element))
            button_group.addButton(button)
            self.toolbar.addWidget(button)

    def _add_toolbar_actions(self):
        for action in Action:
            icon = self.icons.get(action, None)
            button = QToolButton()
            button.setFixedSize(QSize(*self.icon_size))
            button.setIcon(icon)
            func_name = "action_{}".format(action.name.lower())
            func = getattr(self, func_name, None)
            button.clicked.connect(func)
            self.toolbar.addWidget(button)

    def _add_toolbar_toggles(self):
        for toggle in Toggle:
            icon = self.icons.get(toggle, None)
            button = QToolButton()
            button.setFixedSize(QSize(*self.icon_size))
            button.setIcon(icon)
            button.setCheckable(True)
            toggle_name = toggle.name.lower()
            default_value = self.params["builder"]["toggles"][toggle_name]
            func_name = "toggle_{}".format(toggle_name)
            func = getattr(self, func_name, None)
            assert callable(func)
            button.toggled.connect(func)
            button.setChecked(default_value)
            func(default_value)
            self.toolbar.addWidget(button)

    def _add_toolbar_color_button(self):
        self.color_button = ColorButton()
        self.color_button.setFixedSize(QSize(*self.icon_size))
        self.color_button.colorChanged.connect(self.set_block_color)
        self.toolbar.addWidget(self.color_button)
        self.set_block_color(self.default_block_color, is_int=False)

    def load_toolbar(self):
        """Initialize the toolbar."""
        self.toolbar = self.addToolBar("toolbar")
        toolbar_areas = self.params["builder"]["toolbar"]["area"]["range"]
        toolbar_area = self.params["builder"]["toolbar"]["area"]["value"]
        self.addToolBar(
            _get_toolbar_area(toolbar_area, toolbar_areas),
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

    def load_dialogs(self):
        """Load the dialogs."""
        # export dialog
        self.export_dialog = QFileDialog(self)
        self.export_dialog.setWindowTitle("Export")
        self.export_dialog.setNameFilter("Blockset (*.vts *.vtk)")
        self.export_dialog.setWindowIcon(self.icons[Action.EXPORT])
        # XXX: Fails on CI if modal
        # self.export_dialog.setModal(True)

        # import dialog
        self.import_dialog = QFileDialog(self)
        self.import_dialog.setNameFilter("Blockset (*.vts *.vtk)")
        self.import_dialog.setWindowTitle("Import")
        self.import_dialog.setWindowIcon(self.icons[Action.IMPORT])
        # XXX: Fails on CI if modal
        # self.import_dialog.setModal(True)

        # setting dialog
        self.setting_dialog = SettingDialog(self.params, self)
        self.setting_dialog.setWindowIcon(self.icons[Action.SETTING])

        # help dialog
        short_desc = [
            "Build mode",
            "Delete mode",
            "Area selection",
            "Edge visibility",
            "Symmetry Off",
            "Symmetry X",
            "Symmetry Y",
            "Symmetry XY",
            "Reset",
            "Import",
            "Export",
            "Setting",
            "Help",
        ]

        long_desc = [
            "Enable the build mode",
            "Enable the delete mode",
            "Toggle the area selection",
            "Toggle the edge visibility",
            "Disable the symmetry",
            "Enable symmetry along the X axis",
            "Enable symmetry along the Y axis",
            "Enable symmetry along X and Y axis",
            "Reset the scene",
            "Import a blockset",
            "Export a blockset",
            "Open the setting dialog",
            "Open the help dialog",
        ]

        self.help_dialog = HelpDialog(self.icons, self.icon_size, short_desc,
                                      long_desc, self)
        self.help_dialog.setWindowIcon(self.icons[Action.HELP])

    def set_dimensions(self, dimensions):
        """Set the current dimensions."""
        self.dimensions = np.asarray(dimensions)
        self.floor = 0.
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
        self.grid.set_block_mode(value)
        self.selector.set_block_mode(value)
        self.render_scene()

    def set_block_color(self, value=None, is_int=True):
        """Set the current block color."""
        self.block.set_color(value)

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
            self.selector.reset_area()
            self.render_scene()
            return

        if not intersection.element(ElementId.GRID):
            return

        grid_ipoint = intersection.point(ElementId.GRID)

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
        self.color_button.setColor(self.default_block_color, is_int=False)
        self.render_scene()

    def action_import(self, value=None):
        """Import an external blockset."""
        def _import(filename):
            if len(filename) == 0:
                raise ValueError("The input filename string is empty")
            reader = vtk.vtkXMLStructuredGridReader()
            reader.SetFileName(filename)
            reader.Update()
            mesh = reader.GetOutput()
            dimensions = mesh.GetDimensions()
            imported_block = Block(self.params, dimensions, mesh)
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
                    # restore edge visibility
                    self.block.toggle_edges(old_block.show_edges)
                    # restore block mode
                    self.set_block_mode()
                    self.block.merge(old_block)
                    self.block.merge(imported_block)

                    self.selector.hide()
                    self.update_camera()
                self.render_scene()

        if isinstance(value, bool):
            self.import_dialog.fileSelected.connect(_import)
            self.import_dialog.show()
        elif isinstance(value, str):
            _import(value)
        else:
            raise TypeError("Expected type for ``filename``is ``str``"
                            " but {} was given.".format(type(value)))

    def action_export(self, value=None):
        """Export the internal blockset."""
        def _export(filename):
            if len(filename) == 0:
                raise ValueError("The output filename string is empty")
            writer = vtk.vtkXMLStructuredGridWriter()
            writer.SetFileName(filename)
            writer.SetInputData(self.block.mesh)
            writer.Write()

        if isinstance(value, bool):
            self.export_dialog.fileSelected.connect(_export)
            self.export_dialog.show()
        elif isinstance(value, str):
            _export(value)
        else:
            raise TypeError("Expected type for ``filename``is ``str``"
                            " but {} was given.".format(type(value)))

    def action_setting(self, value=None):
        """Open the settings menu."""
        del value
        self.setting_dialog.show()

    def action_help(self, value=None):
        """Display the help menu."""
        del value
        self.help_dialog.show()

    def toggle_area(self, value):
        """Toggle area selection."""
        self.area_selection = value

    def toggle_edges(self, value):
        """Toggle area selection."""
        self.block.toggle_edges(value)
        self.render_scene()


def _get_toolbar_area(area, areas):
    if not isinstance(area, str):
        raise TypeError("Expected type for ``area`` is ``str`` but {}"
                        " was given.".format(type(area)))
    if area not in areas:
        raise ValueError("Expected value for ``area`` in"
                         " {} but {} was given.".format(areas, area))
    area = list(area)
    area[0] = area[0].upper()
    area = ''.join(area)
    area = area + 'ToolBarArea'
    return getattr(QtCore.Qt, area)
