import os.path as op
import enum
import time
from functools import partial
import numpy as np
import vtk

from .params import rcParams
from .graphics import Graphics
from .elements import Element, Symmetry, SymmetrySelector, Grid, Plane, Block


@enum.unique
class BlockMode(enum.Enum):
    BUILD = enum.auto()
    DELETE = enum.auto()
    SELECT = enum.auto()
    CAMERA = enum.auto()
    LIBRARY = enum.auto()
    SETTINGS = enum.auto()
    HELP = enum.auto()


@enum.unique
class Action(enum.Enum):
    RESET = enum.auto()


class Builder(object):
    def __init__(self, dimensions=None, benchmark=None):
        self.unit = rcParams["unit"]
        self.azimuth = rcParams["builder"]["azimuth"]
        self.azimuth_rng = rcParams["builder"]["azimuth_rng"]
        self.elevation_rng = rcParams["builder"]["elevation_rng"]
        self.elevation = rcParams["builder"]["elevation"]
        self.benchmark_dimensions = np.asarray(
            rcParams["builder"]["benchmark"]["dimensions"])
        self.benchmark_number_of_runs = \
            rcParams["builder"]["benchmark"]["number_of_runs"]
        if dimensions is None:
            dimensions = rcParams["builder"]["dimensions"]
        if benchmark is None:
            benchmark = rcParams["builder"]["benchmark"]["enabled"]
        if benchmark:
            self.dimensions = np.asarray(self.benchmark_dimensions)
        else:
            self.dimensions = np.asarray(dimensions)
        self.benchmark = benchmark
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
        self.load_block_modes()
        self.load_interaction()
        self.load_icons()
        self.load_toolbar()
        self.load_benchmark()

        # set initial frame
        self.plotter.reset_camera()
        self.update_camera()
        self.graphics.render()

    def update_camera(self):
        rad_azimuth = _deg2rad(self.azimuth)
        rad_elevation = _deg2rad(self.elevation)

        position = self.grid.center + [
            self.distance * np.cos(rad_azimuth) * np.sin(rad_elevation),
            self.distance * np.sin(rad_azimuth) * np.sin(rad_elevation),
            self.distance * np.cos(rad_elevation)]
        self.plotter.camera.SetPosition(position)
        self.plotter.camera.SetFocalPoint(self.grid.center)

    def move_camera(self, update, inverse=False):
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
        x, y = self.plotter.iren.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)
        self.graphics.render()

    def on_mouse_move(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)

    def on_mouse_wheel_forward(self, vtk_picker, event):
        tr = np.array([0., 0., self.unit])
        if self.grid.origin[2] < self.ceiling:
            self.grid.translate(tr)
            position = np.array(self.plotter.camera.GetPosition())
            self.plotter.camera.SetPosition(position + tr)
            self.plotter.camera.SetFocalPoint(self.grid.center)
        self.graphics.render()

    def on_mouse_wheel_backward(self, vtk_picker, event):
        tr = np.array([0., 0., -self.unit])
        if self.grid.origin[2] > self.floor:
            self.grid.translate(tr)
            position = np.array(self.plotter.camera.GetPosition())
            self.plotter.camera.SetPosition(position + tr)
            self.plotter.camera.SetFocalPoint(self.grid.center)
        self.graphics.render()

    def on_mouse_left_press(self, vtk_picker, event):
        self.button_pressed = True

    def on_mouse_left_release(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)
        self.button_pressed = False

    def on_pick(self, vtk_picker, event):
        func = self.mode_functions.get(self.current_block_mode, None)
        if func is not None:
            func(vtk_picker)

    def load_block_modes(self):
        if not self.benchmark:
            self.set_block_mode(BlockMode.BUILD)
            self.mode_functions = dict()
            for mode in BlockMode:
                func_name = "use_{}_mode".format(mode.name.lower())
                if hasattr(self, func_name):
                    self.mode_functions[mode] = getattr(self, func_name)

    def load_elements(self):
        if self.benchmark:
            show_fps = True
        else:
            show_fps = None
        self.graphics = Graphics(show_fps=show_fps)
        self.plotter = self.graphics.plotter
        self.block = Block(self.plotter, self.dimensions)
        self.grid = Grid(self.plotter, self.dimensions)
        self.plane = Plane(self.plotter, self.dimensions)
        if not self.benchmark:
            self.selector = SymmetrySelector(self.plotter, self.dimensions)
            self.selector.hide()

    def load_interaction(self):
        # allow flexible interactions
        self.plotter._style = vtk.vtkInteractorStyleUser()
        self.plotter.update_style()

        # remove all default key bindings
        self.plotter._key_press_event_callbacks.clear()

        if not self.benchmark:
            # enable cell picking
            self.picker = vtk.vtkCellPicker()
            self.picker.AddObserver(
                vtk.vtkCommand.EndPickEvent,
                self.on_pick
            )

            # setup the key bindings
            self.plotter.iren.AddObserver(
                vtk.vtkCommand.MouseMoveEvent,
                self.on_mouse_move
            )
            self.plotter.iren.AddObserver(
                vtk.vtkCommand.MouseWheelForwardEvent,
                self.on_mouse_wheel_forward
            )
            self.plotter.iren.AddObserver(
                vtk.vtkCommand.MouseWheelBackwardEvent,
                self.on_mouse_wheel_backward
            )
            self.plotter.iren.AddObserver(
                vtk.vtkCommand.LeftButtonPressEvent,
                self.on_mouse_left_press
            )
            self.plotter.iren.AddObserver(
                vtk.vtkCommand.LeftButtonReleaseEvent,
                self.on_mouse_left_release
            )
            self.plotter.add_key_event(
                'Up',
                lambda: self.move_camera(update="distance", inverse=True)
            )
            self.plotter.add_key_event(
                'Down',
                lambda: self.move_camera(update="distance")
            )
            self.plotter.add_key_event(
                'q',
                lambda: self.move_camera(update="azimuth", inverse=True)
            )
            self.plotter.add_key_event(
                'd',
                lambda: self.move_camera(update="azimuth")
            )
            self.plotter.add_key_event(
                'z',
                lambda: self.move_camera(update="elevation", inverse=True)
            )
            self.plotter.add_key_event(
                's',
                lambda: self.move_camera(update="elevation")
            )

    def load_icons(self):
        from PyQt5.Qt import QIcon
        if not self.benchmark:
            self.icons = dict()
            for category in (BlockMode, Action, Symmetry):
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

    def load_toolbar(self):
        if not self.benchmark:
            self.toolbar = self.graphics.window.addToolBar("toolbar")
            self._add_toolbar_group(
                group=BlockMode,
                func=self.set_block_mode,
                default_value=BlockMode.BUILD,
            )
            self.toolbar.addSeparator()
            self._add_toolbar_actions()
            self.toolbar.addSeparator()
            self._add_toolbar_group(
                group=Symmetry,
                func=self.selector.set_symmetry,
                default_value=Symmetry.SYMMETRY_NONE,
            )

    def load_benchmark(self):
        if self.benchmark:
            timings = np.empty(self.benchmark_number_of_runs)
            number_of_blocks = np.prod(self.dimensions - 1)
            for operation in (self.block.add, self.block.remove):
                for run in range(self.benchmark_number_of_runs):
                    start_time = time.perf_counter()
                    for z in range(self.dimensions[2] - 1):
                        for y in range(self.dimensions[1] - 1):
                            for x in range(self.dimensions[0] - 1):
                                # Allow Qt events during benchmark loop
                                self.plotter.app.processEvents()
                                operation([x, y, z])
                    end_time = time.perf_counter()
                    timings[run] = end_time - start_time
                    if operation == self.block.add:
                        self.block.remove_all()
                    else:
                        self.block.add_all()
                print("{}: {:.2f} blk/s".format(operation.__name__,
                                                number_of_blocks /
                                                np.mean(timings)))
            self.plotter.close()

    def set_block_mode(self, value):
        if value in BlockMode:
            self.current_block_mode = value
            if self.grid is not None:
                self.grid.set_block_mode(value)
            if self.selector is not None:
                self.selector.set_block_mode(value)
        self.graphics.render()

    def use_delete_mode(self, vtk_picker):
        self.build_or_delete(vtk_picker, self.block.remove)

    def use_build_mode(self, vtk_picker):
        self.build_or_delete(vtk_picker, self.block.add)

    def build_or_delete(self, vtk_picker, operation):
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

        self.selector.select(coords)
        self.selector.show()
        self.graphics.render()

        if self.button_pressed:
            for coords in self.selector.selection():
                operation(coords)
            self.button_released = False

    def action_reset(self, unused):
        del unused
        self.block.remove_all()
        self.graphics.render()


class Intersection(object):
    def __init__(self, picker):
        self.any_intersection = (picker.GetCellId() != -1)
        if self.any_intersection:
            self.intersections = [None for element in Element]
            self.picked_points = picker.GetPickedPositions()
            self.picked_actors = picker.GetActors()
            for idx, actor in enumerate(self.picked_actors):
                self.intersections[actor.element_id.value] = idx

    def exist(self):
        return self.any_intersection

    def element(self, element_id):
        return self.intersections[element_id.value] is not None

    def point(self, element_id):
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
