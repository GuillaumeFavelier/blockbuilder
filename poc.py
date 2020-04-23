import enum
import numpy as np
import pyvista as pv
import vtk


# default params
rcParams = {
    "unit": 1.,
    "origin": (0., 0., 0.),
    "graphics": {
        "pyvista_menu_bar": False,
        "pyvista_toolbar": False,
        "window_size": (1280, 720),
        "line_width": 2,
        "advanced": True,
        "show_fps": False,
        "fps_position": (2, 2),
        "font_size": 12,
        "background_top_color": (0.05, 0.05, 0.05),
        "background_bottom_color": (0., 0., .35),
    },
    "block": {
        "dimensions": (2, 2, 2),
        "color": (1., 1., 1.),
        "show_edges": True,
        "edge_color": (.1, .1, .1),
        "opacity": 1.,
    },
    "selector": {
        "color": (.3, .3, .8),
        "edge_color": (.4, .4, 1.),
        "opacity": .7,
    },
    "grid": {
        "dimensions": (15, 15, 1),
        "color": (.1, .1, .5),
        "edge_color": (.2, .2, .7),
        "opacity": .7,
    },
    "plane": {
        "dimensions": (15, 15, 1),
        "color": (0.4, 0.4, 0.4),
        "show_edges": False,
    },
}

#################


class Graphics(object):
    def __init__(self, window_size=None, line_width=None, advanced=None,
                 show_fps=None, background_top_color=None,
                 background_bottom_color=None):
        if window_size is None:
            window_size = rcParams["graphics"]["window_size"]
        if line_width is None:
            line_width = rcParams["graphics"]["line_width"]
        if advanced is None:
            advanced = rcParams["graphics"]["advanced"]
        if show_fps is None:
            show_fps = rcParams["graphics"]["show_fps"]
        if background_top_color is None:
            background_top_color = rcParams["graphics"]["background_top_color"]
        if background_bottom_color is None:
            background_bottom_color = \
                rcParams["graphics"]["background_bottom_color"]
        self.window_size = window_size
        self.line_width = line_width
        self.advanced = advanced
        self.show_fps = show_fps
        self.background_top_color = background_top_color
        self.background_bottom_color = background_bottom_color
        self.pyvista_menu_bar = rcParams["graphics"]["pyvista_menu_bar"]
        self.pyvista_toolbar = rcParams["graphics"]["pyvista_toolbar"]
        fps_position = rcParams["graphics"]["fps_position"]
        font_size = rcParams["graphics"]["font_size"]
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
        self.fps = 0
        self.font_size = font_size
        if self.show_fps:
            self.fps_position = fps_position
            self.block_position = np.asarray(self.fps_position) + \
                [0, 2 * self.font_size]
            if self.show_fps:
                self.fps_actor = self.plotter.add_text(
                    "fps: 0", self.fps_position, font_size=self.font_size)
                self.block_actor = self.plotter.add_text(
                    "blocks: 0", self.block_position, font_size=self.font_size)
            self.plotter.add_callback(self.compute_fps)

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

    def compute_fps(self):
        fps = 1.0 / self.plotter.renderer.GetLastRenderTimeInSeconds()
        self.fps = np.round(fps).astype(np.int)
        self.fps_actor.SetInput("fps: {}".format(self.fps))
        self.fps_actor.SetPosition(self.fps_position)
        self.block_actor.SetInput("blocks: {}".format(
            Block.number_of_blocks))
        self.block_actor.SetPosition(self.block_position)


@enum.unique
class Element(enum.Enum):
    BLOCK = 0
    SELECTOR = 1
    GRID = 2
    PLANE = 3


class Block(object):
    number_of_blocks = 0

    def __init__(self, plotter, element_id=None, unit=None, origin=None,
                 dimensions=None, color=None, show_edges=None, edge_color=None,
                 opacity=None):
        if element_id is None:
            element_id = Element.BLOCK
        if unit is None:
            unit = rcParams["unit"]
        if origin is None:
            origin = rcParams["origin"]
        if dimensions is None:
            dimensions = rcParams["block"]["dimensions"]
        if color is None:
            color = rcParams["block"]["color"]
        if show_edges is None:
            show_edges = rcParams["block"]["show_edges"]
        if edge_color is None:
            edge_color = rcParams["block"]["edge_color"]
        if opacity is None:
            opacity = rcParams["block"]["opacity"]
        self.plotter = plotter
        self.element_id = element_id
        self.unit = unit
        self.origin = np.asarray(origin)
        self.color = color
        self.show_edges = show_edges
        self.edge_color = edge_color
        self.opacity = opacity
        self.spacing = [self.unit, self.unit, self.unit]
        self.dimensions = np.asarray(dimensions)
        self.length = self.dimensions * self.spacing
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
        self.mesh = pv.UniformGrid(self.dimensions, self.spacing, self.origin)
        self.actor = self.plotter.add_mesh(
            mesh=self.mesh,
            color=self.color,
            show_edges=self.show_edges,
            edge_color=self.edge_color,
            line_width=rcParams["graphics"]["line_width"],
            opacity=self.opacity,
            reset_camera=False,
        )
        # add data for picking
        self.actor._metadata = self
        if self.element_id is Element.BLOCK:
            Block.number_of_blocks += 1

    def translate(self, tr, update_camera=False):
        # update origin
        self.origin += tr
        self.mesh.SetOrigin(self.origin)

        # update center
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)

        if update_camera:
            position = np.array(self.plotter.camera.GetPosition())
            self.plotter.camera.SetPosition(position + tr)
            self.plotter.camera.SetFocalPoint(self.center)
            self.plotter.render()


class Selector(Block):
    def __init__(self, plotter, element_id=None, unit=None, origin=None,
                 color=None, show_edges=None, edge_color=None, opacity=None):
        if element_id is None:
            element_id = Element.SELECTOR
        if color is None:
            color = rcParams["selector"]["color"]
        if edge_color is None:
            edge_color = rcParams["selector"]["edge_color"]
        if opacity is None:
            opacity = rcParams["selector"]["opacity"]
        super().__init__(
            plotter=plotter,
            element_id=element_id,
            unit=unit,
            origin=origin,
            color=color,
            edge_color=edge_color,
            opacity=opacity,
        )


class Grid(Block):
    def __init__(self, plotter, element_id=None, unit=None, origin=None,
                 dimensions=None, color=None, show_edges=None, edge_color=None,
                 opacity=None):
        if element_id is None:
            element_id = Element.GRID
        if dimensions is None:
            dimensions = rcParams["grid"]["dimensions"]
        if color is None:
            color = rcParams["grid"]["color"]
        if edge_color is None:
            edge_color = rcParams["grid"]["edge_color"]
        if opacity is None:
            opacity = rcParams["grid"]["opacity"]
        super().__init__(
            plotter=plotter,
            element_id=element_id,
            unit=unit,
            origin=origin,
            dimensions=dimensions,
            color=color,
            show_edges=show_edges,
            edge_color=edge_color,
            opacity=opacity,
        )


class Plane(Grid):
    def __init__(self, plotter, element_id=None, unit=None, origin=None,
                 dimensions=None, color=None, show_edges=None):
        if element_id is None:
            element_id = Element.PLANE
        if dimensions is None:
            dimensions = rcParams["plane"]["dimensions"]
        if color is None:
            color = rcParams["plane"]["color"]
        if show_edges is None:
            show_edges = rcParams["plane"]["show_edges"]
        super().__init__(
            plotter=plotter,
            element_id=element_id,
            unit=unit,
            origin=origin,
            dimensions=dimensions,
            color=color,
            show_edges=show_edges,
        )


class Builder(object):
    def __init__(self, unit=None):
        if unit is None:
            unit = rcParams["unit"]
        self.unit = unit
        self.graphics = Graphics()
        self.plotter = self.graphics.plotter
        self.grid = Grid(
            plotter=self.plotter,
            unit=self.unit,
        )
        self.plane = Plane(
            plotter=self.plotter,
            element_id=Element.PLANE,
            unit=self.unit,
        )
        self.selector = Selector(
            plotter=self.plotter,
            unit=self.unit,
        )
        self.plane.actor.VisibilityOff()
        self.selector.actor.VisibilityOff()
        self.plotter.reset_camera()

        self.button_pressed = False
        self.selector_transform = (0, 0, 0)
        self.min_unit = 0.
        self.max_unit = self.grid.dimensions[0] * self.unit
        self.selector_points = self.selector.mesh.points.copy()

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

    def benchmark(self):
        origin = self.grid.origin.copy()
        fps = 0
        for z in range(10):
            for y in range(10):
                for x in range(10):
                    origin[0] = self.grid.origin[0] + x * self.grid.spacing[0]
                    origin[1] = self.grid.origin[1] + y * self.grid.spacing[1]
                    origin[2] = self.grid.origin[2] + z * self.grid.spacing[2]
                    Block(plotter=self.plotter, unit=self.unit, origin=origin)
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
                            unit=self.unit,
                            origin=self.selector_transform,
                        )
                        self.button_released = False
                self.plotter.render()
            elif intersections[Element.PLANE.value]:
                self.selector.actor.VisibilityOff()
        else:
            self.selector.actor.VisibilityOff()


builder = Builder()
