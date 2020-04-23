import numpy as np
import pyvista as pv
import vtk


# default params
rcParams = {
    "unit": 1.,
    "origin": (0., 0., 0.),
    "graphics": {
        "window_size": (1280, 720),
        "pyvista_menu_bar": False,
        "pyvista_toolbar": False,
        "line_width": 2,
        "background_top_color": (0.05, 0.05, 0.05),
        "background_bottom_color": (0., 0., .35),
        "advanced": True,
    },
    "plane": {
        "color": (0.4, 0.4, 0.4),
        "edges": False,
        "opacity": 1.,
    },
    "grid": {
        "color": (.1, .1, .5),
        "resolution": 15,
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


class Graphics(object):
    def __init__(self, window_size=None, line_width=None, advanced=None,
                 background_top_color=None, background_bottom_color=None):
        if window_size is None:
            window_size = rcParams["graphics"]["window_size"]
        if line_width is None:
            line_width = rcParams["graphics"]["line_width"]
        if advanced is None:
            advanced = rcParams["graphics"]["advanced"]
        if background_top_color is None:
            background_top_color = rcParams["graphics"]["background_top_color"]
        if background_bottom_color is None:
            background_bottom_color = \
                rcParams["graphics"]["background_bottom_color"]
        self.window_size = window_size
        self.line_width = line_width
        self.advanced = advanced
        self.background_top_color = background_top_color
        self.background_bottom_color = background_bottom_color
        self.pyvista_menu_bar = rcParams["graphics"]["pyvista_menu_bar"]
        self.pyvista_toolbar = rcParams["graphics"]["pyvista_toolbar"]
        self.plotter = pv.BackgroundPlotter(
            window_size=self.window_size,
            menu_bar=self.pyvista_menu_bar,
            toolbar=self.pyvista_toolbar,
        )
        self.plotter.set_background(
            color=self.background_bottom_color,
            top=self.background_top_color,
        )
        if self.advanced:
            self.plotter.enable_anti_aliasing()
            self.plotter.ren_win.LineSmoothingOn()
        else:
            self.plotter.disable_anti_aliasing()
            self.plotter.ren_win.LineSmoothingOff()

        # remove all default key binding
        self.plotter._key_press_event_callbacks.clear()
        # allow flexible interactions
        self.plotter._style = vtk.vtkInteractorStyleUser()
        self.plotter.update_style()
        # fix the clipping planes being too small
        self.plotter.render = self.render

    def render(self):
        rng = [0] * 6
        self.plotter.renderer.ComputeVisiblePropBounds(rng)
        self.plotter.renderer.ResetCameraClippingRange(rng)
        self.plotter.ren_win.Render()


class Grid(object):
    def __init__(self, plotter, name="grid", unit=None, origin=None,
                 resolution=None, color=None, edges=None, edge_color=None,
                 opacity=None):
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
        self.plotter = plotter
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
        self.actor = self.plotter.add_mesh(
            mesh=self.mesh,
            color=self.color,
            show_edges=self.edges,
            edge_color=self.edge_color,
            line_width=rcParams["graphics"]["line_width"],
            opacity=self.opacity,
        )
        # add data for picking
        self.actor._metadata = self

    def translate(self, tr):
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
        position = np.array(self.plotter.camera.GetPosition())
        self.plotter.camera.SetPosition(position + tr)
        self.plotter.camera.SetFocalPoint(self.center)
        self.plotter.update()


class Block(object):
    def __init__(self, plotter, name="block", unit=None, origin=None,
                 color=None, array=None, edges=None, edge_color=None,
                 opacity=None):
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
        self.plotter = plotter
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
        self.actor = self.plotter.add_mesh(
            mesh=self.mesh,
            show_edges=self.edges,
            edge_color=self.edge_color,
            line_width=rcParams["graphics"]["line_width"],
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
        self.picker.Pick(x, y, 0, self.plotter.renderer)
        self.plotter.update()

    def on_mouse_move(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)

    def on_mouse_wheel_forward(self, vtk_picker, event):
        if self.grid.origin[2] < self.max_unit:
            self.grid.translate([0., 0., self.unit])
        if self.grid.origin[2] > self.min_unit:
            self.plane.actor.VisibilityOn()
            self.plotter.update()

    def on_mouse_wheel_backward(self, vtk_picker, event):
        if self.grid.origin[2] > self.min_unit:
            self.grid.translate([0., 0., -self.unit])
        if self.grid.origin[2] <= self.min_unit:
            self.plane.actor.VisibilityOff()
            self.plotter.update()

    def on_mouse_left_press(self, vtk_picker, event):
        self.button_pressed = True

    def on_mouse_left_release(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, self.plotter.renderer)
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
                        Block(
                            plotter=self.plotter,
                            origin=self.selector_transform
                        )
                        self.button_released = False
                self.plotter.update()
            elif intersections["plane"]:
                self.selector.actor.VisibilityOff()
        else:
            self.selector.actor.VisibilityOff()


graphics = Graphics()
grid = Grid(plotter=graphics.plotter)
plane = Grid(
    plotter=graphics.plotter,
    name="plane",
    color=rcParams["plane"]["color"],
    edges=rcParams["plane"]["edges"],
    opacity=rcParams["plane"]["opacity"],
)
plane.actor.VisibilityOff()
selector = Block(
    plotter=graphics.plotter,
    name="selector",
    color=rcParams["selector"]["color"],
    edge_color=rcParams["selector"]["edge_color"],
    opacity=rcParams["selector"]["opacity"],
)
selector.actor.VisibilityOff()
builder = Builder(graphics.plotter, grid, plane, selector)
