import enum
import os.path as op
from functools import partial
import numpy as np
import pyvista as pv
import vtk

from .params import rcParams
from .graphics import Graphics
from .block import Selector, Grid, Plane


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
    SELECT = enum.auto()
    CAMERA = enum.auto()
    LIBRARY = enum.auto()
    SETTINGS = enum.auto()
    HELP = enum.auto()


class Builder(object):
    def __init__(self, unit=None, dimensions=None, benchmark=None):
        if unit is None:
            unit = rcParams["unit"]
        if dimensions is None:
            dimensions = rcParams["builder"]["dimensions"]
        if benchmark is None:
            benchmark = rcParams["builder"]["benchmark"]
        self.unit = unit
        self.dimensions = dimensions
        self.benchmark = benchmark
        self.button_pressed = False
        self.floor = 0.
        self.ceiling = self.dimensions[2] * self.unit
        self.icons = None
        self.graphics = None
        self.plotter = None
        self.toolbar = None
        self.picker = None
        self.current_mode = None
        self.mode_functions = None

        # configuration
        self.configure_modes()
        self.configure_elements()
        self.configure_interaction()
        self.configure_icons()
        self.configure_toolbar()
        self.configure_benchmark()

        # experiment:
        class MetaData(object):
            def __init__(self, element_id):
                self.element_id = element_id

        self.cgrid = pv.StructuredGrid()
        points = vtk.vtkPoints()
        for k in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                for i in range(self.dimensions[2]):
                    points.InsertNextPoint(i, j, k)

        self.cgrid.SetDimensions(self.dimensions)
        self.cgrid.SetPoints(points)
        cgrid_color = (1., 1., 1.)
        number_of_cells = self.cgrid.GetNumberOfCells()
        self.cgrid.cell_arrays["color"] = np.tile(
           cgrid_color,
           (number_of_cells, 1),
        )
        for cell_id in range(number_of_cells):
            self.cgrid.BlankCell(cell_id)
        actor = self.plotter.add_mesh(
            self.cgrid,
            scalars="color",
            rgb=True,
            line_width=rcParams["graphics"]["line_width"],
            show_edges=True,
            show_scalar_bar=False,
        )
        actor._metadata = MetaData(Element.BLOCK)

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
        if self.grid.origin[2] < self.ceiling:
            self.grid.translate([0., 0., self.unit], update_camera=True)
        if self.grid.origin[2] > self.floor:
            self.plane.actor.VisibilityOn()
            self.plotter.render()

    def on_mouse_wheel_backward(self, vtk_picker, event):
        if self.grid.origin[2] > self.floor:
            self.grid.translate([0., 0., -self.unit], update_camera=True)
        if self.grid.origin[2] <= self.floor:
            self.plane.actor.VisibilityOff()
            self.plotter.render()

    def on_mouse_left_press(self, vtk_picker, event):
        self.button_pressed = True

    def on_mouse_left_release(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)
        self.button_pressed = False

    def on_pick(self, vtk_picker, event):
        func = self.mode_functions.get(self.current_mode, None)
        if func is not None:
            func(vtk_picker)

    def configure_modes(self):
        if not self.benchmark:
            self.set_mode(InteractionMode.BUILD)
            self.mode_functions = dict()
            for mode in InteractionMode:
                func_name = "use_{}_mode".format(mode.name.lower())
                if hasattr(self, func_name):
                    self.mode_functions[mode] = getattr(self, func_name)

    def configure_elements(self):
        if self.benchmark:
            show_fps = True
        else:
            show_fps = None
        self.graphics = Graphics(show_fps=show_fps)
        self.plotter = self.graphics.plotter
        grid_dimensions = [
            self.dimensions[0],
            self.dimensions[1],
            1
        ]
        self.grid = Grid(
            plotter=self.plotter,
            element_id=Element.GRID,
            dimensions=grid_dimensions,
            unit=self.unit,
        )
        if not self.benchmark:
            self.plane = Plane(
                plotter=self.plotter,
                element_id=Element.PLANE,
                dimensions=grid_dimensions,
                unit=self.unit,
            )
            self.plane.actor.VisibilityOff()
            self.selector = Selector(
                plotter=self.plotter,
                element_id=Element.SELECTOR,
                unit=self.unit,
            )
            self.selector.actor.VisibilityOff()
        self.plotter.reset_camera()

    def configure_interaction(self):
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

    def configure_icons(self):
        from PyQt5.Qt import QIcon
        if not self.benchmark:
            self.icons = dict()
            for mode in InteractionMode:
                icon_path = "icons/{}.svg".format(mode.name.lower())
                if op.isfile(icon_path):
                    self.icons[mode] = QIcon(icon_path)

    def configure_toolbar(self):
        from PyQt5.QtWidgets import QToolButton, QButtonGroup
        if not self.benchmark:
            self.toolbar = self.graphics.window.addToolBar("toolbar")
            self.mode_buttons = QButtonGroup()
            for mode in InteractionMode:
                icon = self.icons.get(mode, None)
                if icon is not None:
                    button = QToolButton()
                    button.setIcon(icon)
                    button.setCheckable(True)
                    if mode is self.current_mode:
                        button.setChecked(True)
                    button.toggled.connect(partial(self.set_mode, mode=mode))
                    self.mode_buttons.addButton(button)
                    self.toolbar.addWidget(button)

    def configure_benchmark(self):
        if self.benchmark:
            fps = 0
            box = pv.Box(bounds=(-.5, .5, -.5, .5, -.5, .5))
            dataset = pv.PolyData()
            points = vtk.vtkPoints()
            dataset.SetPoints(points)
            alg = vtk.vtkGlyph3D()
            alg.SetSourceData(box)
            alg.SetInputData(dataset)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(alg.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            self.plotter.renderer.AddActor(actor)
            for z in range(14):
                for y in range(14):
                    for x in range(14):
                        # Allow Qt events during benchmark loop (i.e. fps)
                        self.plotter.app.processEvents()
                        steps = np.array([x, y, z])
                        origin = self.grid.origin + np.multiply(
                            steps, self.grid.spacing)
                        points.InsertNextPoint(origin)
                        points.Modified()
                        fps += self.graphics.fps
            print(fps / 1000.0)
            self.plotter.close()

    def set_mode(self, mode):
        if mode in InteractionMode:
            self.current_mode = mode

    def use_delete_mode(self, vtk_picker):
        any_intersection = (vtk_picker.GetCellId() != -1)
        if not any_intersection:
            self.selector.actor.VisibilityOff()
            return

        intersections = self.compute_intersection_table(vtk_picker)
        if intersections[Element.GRID.value] is None:
            return

        picked_points = vtk_picker.GetPickedPositions()
        grid_idata = intersections[Element.GRID.value]
        grid_ipoint = np.asarray(picked_points.GetPoint(grid_idata))

        coords = np.floor(grid_ipoint / self.unit)
        coords[2] = self.grid.origin[2] / self.unit

        selector_origin = coords * self.unit
        self.selector.mesh.SetOrigin(selector_origin)
        self.selector.actor.VisibilityOn()

        coords = coords.astype(np.int)
        cell_id = _coords_to_cell(coords, self.dimensions)
        if self.button_pressed:
            self.button_released = False
            if intersections[Element.BLOCK.value] is not None and self.cgrid.IsCellVisible(cell_id):
                self.cgrid.BlankCell(cell_id)
                self.cgrid.Modified()
        self.plotter.render()

    def use_build_mode(self, vtk_picker):
        any_intersection = (vtk_picker.GetCellId() != -1)
        if not any_intersection:
            self.selector.actor.VisibilityOff()
            return

        intersections = self.compute_intersection_table(vtk_picker)
        if intersections[Element.GRID.value] is None:
            return

        picked_points = vtk_picker.GetPickedPositions()
        grid_idata = intersections[Element.GRID.value]
        grid_ipoint = np.asarray(picked_points.GetPoint(grid_idata))

        coords = np.floor(grid_ipoint / self.unit)
        coords[2] = self.grid.origin[2] / self.unit

        selector_origin = coords * self.unit
        self.selector.mesh.SetOrigin(selector_origin)
        self.selector.actor.VisibilityOn()

        coords = coords.astype(np.int)
        cell_id = _coords_to_cell(coords, self.dimensions)
        if self.button_pressed:
            self.button_released = False
            if intersections[Element.BLOCK.value] is not None and self.cgrid.IsCellVisible(cell_id):
                pass
            else:
                self.cgrid.UnBlankCell(cell_id)
                self.cgrid.Modified()
        self.plotter.render()

    def compute_intersection_table(self, vtk_picker):
        picked_actors = vtk_picker.GetActors()
        intersections = [None for element in Element]
        for idx, actor in enumerate(picked_actors):
            intersections[actor._metadata.element_id.value] = idx
        return intersections


def _coords_to_cell(coords, dimensions):
    cell_id = coords[0] + \
        coords[1] * (dimensions[0] - 1) + \
        coords[2] * (dimensions[0] - 1) * (dimensions[1] - 1)
    return cell_id
