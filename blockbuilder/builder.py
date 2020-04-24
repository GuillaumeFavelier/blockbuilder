import enum
from functools import partial
import numpy as np
import vtk

from .params import rcParams
from .graphics import Graphics
from .block import Block, Selector, Grid, Plane


@enum.unique
class Element(enum.Enum):
    BLOCK = 0
    SELECTOR = 1
    GRID = 2
    PLANE = 3


@enum.unique
class InteractionMode(enum.Enum):
    BUILD = enum.auto()
    DELETE = enum.auto()
    # CAMERA = enum.auto()
    # SELECT = enum.auto()
    # LIBRARY = enum.auto()
    # SETTINGS = enum.auto()
    # HELP = enum.auto()


class Builder(object):
    def __init__(self, unit=None):
        if unit is None:
            unit = rcParams["unit"]
        self.unit = unit
        self.icons = dict()
        self.set_mode(InteractionMode.BUILD)
        self.mode_functions = {
            mode: getattr(self, "use_{}_mode".format(mode.name.lower()))
            for mode in InteractionMode
        }
        self.graphics = Graphics()
        self.plotter = self.graphics.plotter
        self.grid = Grid(
            plotter=self.plotter,
            element_id=Element.GRID,
            unit=self.unit,
        )
        self.plane = Plane(
            plotter=self.plotter,
            element_id=Element.PLANE,
            unit=self.unit,
        )
        self.selector = Selector(
            plotter=self.plotter,
            element_id=Element.SELECTOR,
            unit=self.unit,
        )
        self.plane.actor.VisibilityOff()
        self.selector.actor.VisibilityOff()
        self.plotter.reset_camera()

        self.button_pressed = False
        self.selector_transform = (0, 0, 0)
        self.min_unit = 0.
        self.max_unit = self.grid.dimensions[0] * self.unit

        iren = self.plotter.iren
        iren.AddObserver(
            vtk.vtkCommand.MouseMoveEvent,
            self.on_mouse_move
        )
        iren.AddObserver(
            vtk.vtkCommand.MouseWheelForwardEvent,
            self.on_mouse_wheel_forward
        )
        iren.AddObserver(
            vtk.vtkCommand.MouseWheelBackwardEvent,
            self.on_mouse_wheel_backward
        )
        iren.AddObserver(
            vtk.vtkCommand.LeftButtonPressEvent,
            self.on_mouse_left_press
        )
        iren.AddObserver(
            vtk.vtkCommand.LeftButtonReleaseEvent,
            self.on_mouse_left_release
        )

        self.plotter.add_key_event(
            'Up',
            lambda: self.move_camera(self.unit)
        )
        self.plotter.add_key_event(
            'Down',
            lambda: self.move_camera(-self.unit)
        )
        self.plotter.add_key_event(
            'q',
            lambda: self.move_camera(self.unit,
                                     tangential=True)
        )
        self.plotter.add_key_event(
            'd',
            lambda: self.move_camera(-self.unit,
                                     tangential=True)
        )
        self.plotter.add_key_event(
            'z',
            lambda: self.move_camera(self.unit,
                                     tangential=True, inverse=True)
        )
        self.plotter.add_key_event(
            's',
            lambda: self.move_camera(-self.unit,
                                     tangential=True, inverse=True)
        )

        self.picker = vtk.vtkCellPicker()
        self.picker.AddObserver(
            vtk.vtkCommand.EndPickEvent,
            self.on_pick
        )

        self.toolbar = rcParams["builder"]["toolbar"]
        self.toolbar_widget = None
        self.actions = dict()

        # configuration
        self.configure_icons()
        self.configure_toolbar()

    def benchmark(self):
        origin = self.grid.origin.copy()
        fps = 0
        for z in range(10):
            for y in range(10):
                for x in range(10):
                    origin[0] = self.grid.origin[0] + x * self.grid.spacing[0]
                    origin[1] = self.grid.origin[1] + y * self.grid.spacing[1]
                    origin[2] = self.grid.origin[2] + z * self.grid.spacing[2]
                    Block(
                        plotter=self.plotter,
                        element_id=Element.BLOCK,
                        unit=self.unit,
                        origin=origin
                    )
                    fps += self.graphics.fps
        print(fps / 1000.0)

    def move_camera(self, move_factor, tangential=False, inverse=False):
        position = np.array(self.plotter.camera.GetPosition())
        focal_point = np.array(self.plotter.camera.GetFocalPoint())
        move_vector = focal_point - position
        move_vector /= np.linalg.norm(move_vector)
        if tangential:
            viewup = np.array(self.plotter.camera.GetViewUp())
            tanget_vector = np.cross(viewup, move_vector)
            if inverse:
                move_vector = np.cross(move_vector, tanget_vector)
            else:
                move_vector = tanget_vector

        move_vector *= move_factor
        position += move_vector
        self.plotter.camera.SetPosition(position)
        # update pick
        x, y = self.plotter.iren.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)
        self.plotter.render()

    def on_mouse_move(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)

    def on_mouse_wheel_forward(self, vtk_picker, event):
        if self.grid.origin[2] < self.max_unit:
            self.grid.translate([0., 0., self.unit], update_camera=True)
        if self.grid.origin[2] > self.min_unit:
            self.plane.actor.VisibilityOn()
            self.plotter.render()

    def on_mouse_wheel_backward(self, vtk_picker, event):
        if self.grid.origin[2] > self.min_unit:
            self.grid.translate([0., 0., -self.unit], update_camera=True)
        if self.grid.origin[2] <= self.min_unit:
            self.plane.actor.VisibilityOff()
            self.plotter.render()

    def on_mouse_left_press(self, vtk_picker, event):
        self.button_pressed = True

    def on_mouse_left_release(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)
        self.button_pressed = False

    def on_pick(self, vtk_picker, event):
        self.mode_functions[self.mode](vtk_picker)

    def configure_icons(self):
        from PyQt5.Qt import QIcon
        self.icons[InteractionMode.BUILD] = \
            QIcon("icons/add_box-black-48dp.svg")
        self.icons[InteractionMode.DELETE] = \
            QIcon("icons/remove_circle_outline-black-48dp.svg")

    def configure_toolbar(self):
        from PyQt5.QtWidgets import QToolButton, QButtonGroup
        if self.toolbar:
            self.toolbar_widget = self.graphics.window.addToolBar("toolbar")
            self.mode_buttons = QButtonGroup()
            for mode in InteractionMode:
                button = QToolButton()
                button.setIcon(self.icons[mode])
                button.setCheckable(True)
                if mode is self.mode:
                    button.setChecked(True)
                button.toggled.connect(partial(self.set_mode, mode=mode))
                self.mode_buttons.addButton(button)
                self.toolbar_widget.addWidget(button)

    def set_mode(self, mode):
        if mode in InteractionMode:
            self.mode = mode

    def use_delete_mode(self, vtk_picker):
        any_intersection = (vtk_picker.GetCellId() != -1)
        if any_intersection:
            actors = vtk_picker.GetActors()
            points = vtk_picker.GetPickedPositions()
            intersections = [False for element in Element]
            for idx, actor in enumerate(actors):
                intersections[actor._metadata.element_id.value] = (idx, actor)

            if intersections[Element.GRID.value]:
                grid_idata = intersections[Element.GRID.value]
                # draw the selector
                point = np.asarray(points.GetPoint(grid_idata[0]))
                pt_min = np.floor(point / self.unit) * self.unit
                pt_min[-1] = self.grid.origin[2]
                center = pt_min
                self.selector_transform = center
                self.selector.mesh.SetOrigin(center)
                self.selector.actor.VisibilityOn()
                if self.button_pressed:
                    if intersections[Element.BLOCK.value]:
                        block_idata = intersections[Element.BLOCK.value]
                        block_metadata = block_idata[1]._metadata
                        if block_metadata.origin[2] == self.grid.origin[2]:
                            self.plotter.remove_actor(block_metadata.actor)
                self.plotter.render()
            elif intersections[Element.PLANE.value]:
                self.selector.actor.VisibilityOff()
        else:
            self.selector.actor.VisibilityOff()

    def use_build_mode(self, vtk_picker):
        any_intersection = (vtk_picker.GetCellId() != -1)
        if any_intersection:
            actors = vtk_picker.GetActors()
            points = vtk_picker.GetPickedPositions()
            intersections = [False for element in Element]
            for idx, actor in enumerate(actors):
                intersections[actor._metadata.element_id.value] = (idx, actor)

            if intersections[Element.GRID.value]:
                grid_idata = intersections[Element.GRID.value]
                # draw the selector
                point = np.asarray(points.GetPoint(grid_idata[0]))
                pt_min = np.floor(point / self.unit) * self.unit
                pt_min[-1] = self.grid.origin[2]
                center = pt_min
                self.selector_transform = center
                self.selector.mesh.SetOrigin(center)
                self.selector.actor.VisibilityOn()
                add_block = True
                if intersections[Element.BLOCK.value]:
                    block_idata = intersections[Element.BLOCK.value]
                    block_metadata = block_idata[1]._metadata
                    if block_metadata.origin[2] == self.grid.origin[2]:
                        add_block = False

                if add_block:
                    if self.button_pressed:
                        Block(
                            plotter=self.plotter,
                            element_id=Element.BLOCK,
                            unit=self.unit,
                            origin=self.selector_transform,
                        )
                        self.button_released = False
                self.plotter.render()
            elif intersections[Element.PLANE.value]:
                self.selector.actor.VisibilityOff()
        else:
            self.selector.actor.VisibilityOff()
