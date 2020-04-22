import numpy as np
import pyvista as pv
import vtk


# default params
rcParams = {
    "background_color_top": (0.05, 0.05, 0.05),
    "background_color_bottom": (0., 0., .35),
    "plane_color": (.3, .3, .3),
    "grid_color": (.1, .1, .7),
    "selector_color": (.1, .1, .7),
    "block_color": (1., 1., 1.),
}

#################

# plane
plane_size = 20
plane = pv.Plane(center=(5, 5, -1.),
                 i_size=plane_size, j_size=plane_size,
                 i_resolution=1, j_resolution=1)

# grid
grid_size = 10
grid_length = (grid_size - 1) ** 2
grid = pv.UniformGrid()
grid.dimensions = (grid_size, grid_size, 1)

# selector
selector = pv.Box(bounds=(0, 1.0, 0, 1.0, 0, 1.0))
selector_points = selector.points.copy()
selector_offset = (-.5, -.5, 0)
selector_scalars = np.tile(rcParams["selector_color"], (6, 1))
selector.cell_arrays["color"] = selector_scalars

# plotter
plotter = pv.BackgroundPlotter(menu_bar=False, toolbar=False)
plotter.set_background(
    color=rcParams["background_color_bottom"],
    top=rcParams["background_color_top"],
)
plotter.enable_anti_aliasing()
plotter._key_press_event_callbacks.clear()
plotter._style = vtk.vtkInteractorStyleUser()
plotter.update_style()

plane_actor = plotter.add_mesh(
    plane,
    show_edges=True,
    color=rcParams["plane_color"],
)
plane_actor._mesh = plane
plane_actor._name = "plane"
grid_actor = plotter.add_mesh(
    grid,
    show_edges=True,
    color=rcParams["grid_color"],
    opacity=0.7
)
grid_actor._mesh = grid
grid_actor._name = "grid"
selector_actor = plotter.add_mesh(
    selector,
    show_edges=True,
    scalars="color",
    rgb=True,
    opacity=0.7
)
selector_actor._mesh = selector
selector_actor._name = "selector"
selector_actor.VisibilityOff()


class Builder(object):
    def __init__(self, plotter):
        self.plotter = plotter
        self.button_pressed = False
        self.selector_transform = (0, 0, 0)
        self.grid_zpos = 0

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

        self.picker = vtk.vtkCellPicker()
        self.picker.AddObserver(
            vtk.vtkCommand.EndPickEvent,
            self.on_pick
        )

    def on_mouse_move(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, plotter.renderer)

    def on_mouse_wheel_forward(self, vtk_picker, event):
        if self.grid_zpos < grid_length:
            grid.translate((0, 0, 1))
            self.grid_zpos += 1

    def on_mouse_wheel_backward(self, vtk_picker, event):
        if self.grid_zpos > 0:
            grid.translate((0, 0, -1))
            self.grid_zpos -= 1

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
                intersections[actor._name] = (idx, actor)

            if intersections["grid"]:
                grid_data = intersections["grid"]
                # draw the selector
                point = points.GetPoint(grid_data[0])
                pt_min = np.floor(point).astype(np.int)
                pt_min[-1] = self.grid_zpos
                center = pt_min + [0.5, 0.5, 0]
                self.selector_transform = center + selector_offset
                selector.points = selector_points.copy()
                selector.translate(self.selector_transform)
                selector_actor.VisibilityOn()
                add_block = True
                if intersections["block"]:
                    block_data = intersections["block"]
                    if block_data[1]._zpos == self.grid_zpos:
                        add_block = False

                if add_block:
                    if self.button_pressed:
                        block = pv.Box(bounds=(0, 1.0, 0, 1.0, 0, 1.0))
                        block_scalars = np.tile(
                            rcParams["block_color"],
                            (6, 1)
                        )
                        block.cell_arrays["color"] = block_scalars
                        block.translate(self.selector_transform)
                        block_actor = plotter.add_mesh(
                            block, show_edges=True, reset_camera=False,
                            scalars="color", rgb=True
                        )
                        block._transform = self.selector_transform
                        block_actor._mesh = block
                        block_actor._name = "block"
                        block_actor._zpos = self.grid_zpos
                        self.button_released = False
                plotter.update()
            elif intersections["plane"]:
                selector_actor.VisibilityOff()

            if intersections["block"]:
                block_data = intersections["block"]
                if block_data[0] == 1:
                    mesh = block_data[1]._mesh
                    self.selector_transform = mesh._transform
                    selector.points = selector_points.copy()
                    selector.translate(self.selector_transform)
                    selector_actor.VisibilityOn()
                    plotter.update()
        else:
            selector_actor.VisibilityOff()


builder = Builder(plotter)
