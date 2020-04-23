import numpy as np
import pyvista as pv
import vtk


# default params
rcParams = {
    "unit": 1.,
    "origin": (0., 0., 0.),
    "line_width": 2,
    "background": {
        "top_color": (0.05, 0.05, 0.05),
        "bottom_color": (0., 0., .35),
    },
    "plane": {
        "color": (0.4, 0.4, 0.4),
        "edges": False,
        "opacity": 1.,
    },
    "grid": {
        "color": (.1, .1, .5),
        "resolution": 30,
        "edges": True,
        "edge_color": (.2, .2, .7),
        "opacity": .7,
    },
    "selector": {
        "color": (.3, .3, .8),
        "edge_color": (.4, .4, 1.),
        "opacity": .7,
    },
    "block": {
        "array": "color",
        "color": (1., 1., 1.),
        "edges": True,
        "edge_color": (.1, .1, .1),
        "opacity": 1.,
    },
}
rcParams["camera_move_factor"] = rcParams["unit"]

#################

# plotter
plotter = pv.BackgroundPlotter(menu_bar=False, toolbar=False)
plotter.set_background(
    color=rcParams["background"]["bottom_color"],
    top=rcParams["background"]["top_color"],
)
plotter._key_press_event_callbacks.clear()
plotter._style = vtk.vtkInteractorStyleUser()
plotter.update_style()
# graphics
plotter.enable_anti_aliasing()
plotter.ren_win.LineSmoothingOn()


def _render():
    rng = [0] * 6
    plotter.renderer.ComputeVisiblePropBounds(rng)
    plotter.renderer.ResetCameraClippingRange(rng)
    plotter.ren_win.Render()


plotter.render = _render


class Grid(object):
    def __init__(self, name="grid", unit=None, origin=None, resolution=None,
                 color=None, edges=None, edge_color=None, opacity=None):
        if unit is None:
            unit = rcParams["unit"]
        if origin is None:
            origin = rcParams["origin"]
        if resolution is None:
            resolution = rcParams["grid"]["resolution"]
        if color is None:
            color = rcParams["grid"]["color"]
        if edges is None:
            edges = rcParams["grid"]["edges"]
        if edge_color is None:
            edge_color = rcParams["grid"]["edge_color"]
        if opacity is None:
            opacity = rcParams["grid"]["opacity"]
        self.name = name
        self.unit = unit
        self.origin = np.asarray(origin)
        self.resolution = resolution
        self.color = color
        self.edges = edges
        self.edge_color = edge_color
        self.opacity = opacity
        self.spacing = [self.unit, self.unit, self.unit]
        self.length = self.resolution * self.spacing
        self.dimensions = (self.resolution, self.resolution, 1)
        self.center = (
            self.origin[0] + (self.resolution/2.) * self.spacing[0],
            self.origin[1] + (self.resolution/2.) * self.spacing[1],
            self.origin[2],
        )
        self.mesh = pv.UniformGrid(self.dimensions, self.spacing, self.origin)
        self.actor = plotter.add_mesh(
            mesh=self.mesh,
            color=self.color,
            show_edges=self.edges,
            edge_color=self.edge_color,
            line_width=rcParams["line_width"],
            opacity=self.opacity,
        )
        # add data for picking
        self.actor._metadata = self

    def translate(self, tr, plotter):
        # update origin
        self.origin += tr
        self.mesh.SetOrigin(self.origin)

        # update center
        self.center = (
            self.origin[0] + (self.resolution/2.) * self.spacing[0],
            self.origin[1] + (self.resolution/2.) * self.spacing[1],
            self.origin[2],
        )

        # update camera
        position = np.array(plotter.camera.GetPosition())
        plotter.camera.SetPosition(position + tr)
        plotter.camera.SetFocalPoint(self.center)
        plotter.update()


class Block(object):
    def __init__(self, name="block", unit=None, origin=None, color=None,
                 array=None, edges=None, edge_color=None, opacity=None):
        if unit is None:
            unit = rcParams["unit"]
        if origin is None:
            origin = rcParams["origin"]
        if color is None:
            color = rcParams["block"]["color"]
        if array is None:
            array = rcParams["block"]["array"]
        if edges is None:
            edges = rcParams["block"]["edges"]
        if edge_color is None:
            edge_color = rcParams["block"]["edge_color"]
        if opacity is None:
            opacity = rcParams["block"]["opacity"]
        self.name = name
        self.unit = unit
        self.origin = origin
        self.bounds = (
            self.origin[0], self.origin[0] + self.unit,
            self.origin[1], self.origin[1] + self.unit,
            self.origin[2], self.origin[2] + self.unit,
        )
        self.color = color
        self.array = array
        self.edges = edges
        self.edge_color = edge_color
        self.opacity = opacity
        self.scalars = np.tile(self.color, (6, 1))
        self.mesh = pv.Box(bounds=self.bounds)
        self.mesh.cell_arrays[self.array] = self.scalars
        self.actor = plotter.add_mesh(
            mesh=self.mesh,
            show_edges=self.edges,
            edge_color=self.edge_color,
            line_width=rcParams["line_width"],
            opacity=self.opacity,
            scalars=self.array,
            rgb=True,
            reset_camera=False,
        )
        # add data for picking
        self.actor._metadata = self


class Builder(object):
    def __init__(self, plotter, grid, plane, selector, unit=None):
        if unit is None:
            unit = rcParams["unit"]
        self.unit = unit
        self.plotter = plotter
        self.grid = grid
        self.plane = plane
        self.selector = selector

        self.button_pressed = False
        self.selector_transform = (0, 0, 0)
        self.min_unit = 0.
        self.max_unit = self.grid.resolution * self.unit
        self.selector_points = selector.mesh.points.copy()

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
            lambda: self.move_camera(rcParams["camera_move_factor"])
        )
        self.plotter.add_key_event(
            'Down',
            lambda: self.move_camera(-rcParams["camera_move_factor"])
        )
        self.plotter.add_key_event(
            'q',
            lambda: self.move_camera(rcParams["camera_move_factor"],
                                     tangential=True)
        )
        self.plotter.add_key_event(
            'd',
            lambda: self.move_camera(-rcParams["camera_move_factor"],
                                     tangential=True)
        )
        self.plotter.add_key_event(
            'z',
            lambda: self.move_camera(rcParams["camera_move_factor"],
                                     tangential=True, inverse=True)
        )
        self.plotter.add_key_event(
            's',
            lambda: self.move_camera(-rcParams["camera_move_factor"],
                                     tangential=True, inverse=True)
        )

        self.picker = vtk.vtkCellPicker()
        self.picker.AddObserver(
            vtk.vtkCommand.EndPickEvent,
            self.on_pick
        )

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
        self.picker.Pick(x, y, 0, plotter.renderer)
        self.plotter.update()

    def on_mouse_move(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, plotter.renderer)

    def on_mouse_wheel_forward(self, vtk_picker, event):
        if self.grid.origin[2] < self.max_unit:
            self.grid.translate([0., 0., self.unit], plotter)
        if self.grid.origin[2] > self.min_unit:
            self.plane.actor.VisibilityOn()
            self.plotter.update()

    def on_mouse_wheel_backward(self, vtk_picker, event):
        if self.grid.origin[2] > self.min_unit:
            self.grid.translate([0., 0., -self.unit], plotter)
        if self.grid.origin[2] <= self.min_unit:
            self.plane.actor.VisibilityOff()
            self.plotter.update()

    def on_mouse_left_press(self, vtk_picker, event):
        self.button_pressed = True

    def on_mouse_left_release(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, plotter.renderer)
        self.button_pressed = False

    def on_pick(self, vtk_picker, event):
        any_intersection = (vtk_picker.GetCellId() != -1)
        if any_intersection:
            intersections = {
                "grid": False,
                "selector": False,
                "block": False,
                "plane": False,
            }
            actors = vtk_picker.GetActors()
            points = vtk_picker.GetPickedPositions()
            for idx, actor in enumerate(actors):
                intersections[actor._metadata.name] = (idx, actor)

            if intersections["grid"]:
                grid_data = intersections["grid"]
                # draw the selector
                point = np.asarray(points.GetPoint(grid_data[0]))
                pt_min = np.floor(point / self.unit) * self.unit
                pt_min[-1] = self.grid.origin[2]
                center = pt_min
                self.selector_transform = center
                selector.mesh.points = self.selector_points.copy()
                selector.mesh.translate(self.selector_transform)
                selector.actor.VisibilityOn()
                add_block = True
                if intersections["block"]:
                    block_data = intersections["block"][1]._metadata
                    if block_data.origin[2] == self.grid.origin[2]:
                        add_block = False

                if add_block:
                    if self.button_pressed:
                        Block(origin=self.selector_transform)
                        self.button_released = False
                plotter.update()
            elif intersections["plane"]:
                self.selector.actor.VisibilityOff()
        else:
            self.selector.actor.VisibilityOff()


grid = Grid()
plane = Grid(
    name="plane",
    color=rcParams["plane"]["color"],
    edges=rcParams["plane"]["edges"],
    opacity=rcParams["plane"]["opacity"],
)
plane.actor.VisibilityOff()
selector = Block(
    name="selector",
    color=rcParams["selector"]["color"],
    edge_color=rcParams["selector"]["edge_color"],
    opacity=rcParams["selector"]["opacity"],
)
selector.actor.VisibilityOff()
builder = Builder(plotter, grid, plane, selector)
