import numpy as np
import pyvista as pv
import vtk

# background
background_color1 = (0.05, 0.05, 0.05)
background_color2 = (0., 0., .35)

# plane
plane_color = (.3, .3, .3)
plane_size = 20
plane = pv.Plane(center=(5, 5, -0.0001),
                 i_size=plane_size, j_size=plane_size,
                 i_resolution=1, j_resolution=1)

# grid
grid_color = (.1, .1, .7)
grid_size = 10
grid_length = (grid_size - 1) ** 2
grid = pv.UniformGrid()
grid.dimensions = (grid_size, grid_size, 1)
grid._name = "GRID"

# box
box = pv.Box(bounds=(0, 1.0, 0, 1.0, 0, 1.0))
box_points = box.points.copy()
box_offset = (-.5, -.5, 0)
box_color = (.1, .1, .7)
box_scalars = np.tile(box_color, (6, 1))
box.cell_arrays["color"] = box_scalars

# plotter
plotter = pv.BackgroundPlotter(menu_bar=False, toolbar=False)
plotter.set_background(background_color2, top=background_color1)
plotter.enable_anti_aliasing()
plotter._key_press_event_callbacks.clear()
plotter._style = vtk.vtkInteractorStyleUser()
plotter.update_style()

plotter.add_mesh(plane, show_edges=True, color=plane_color)
plotter.add_mesh(grid, show_edges=True, color=grid_color, opacity=0.7)
box_actor = plotter.add_mesh(box, show_edges=True, scalars="color",
                             rgb=True, opacity=0.7)
box_actor.VisibilityOff()


class Builder(object):
    def __init__(self, plotter):
        self.plotter = plotter
        self.box_transform = (0, 0, 0)
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
            self.on_left_click
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

    def on_left_click(self, vtk_picker, event):
        if self.last_pick == "GRID":
            fixed_box = pv.Box(bounds=(0, 1.0, 0, 1.0, 0, 1.0))
            fixed_box_color = (1., 1., 1.)
            fixed_box_scalars = np.tile(fixed_box_color, (6, 1))
            fixed_box.cell_arrays["color"] = fixed_box_scalars
            fixed_box.translate(self.box_transform)
            actor = plotter.add_mesh(fixed_box, show_edges=True,
                                     reset_camera=False,
                                     scalars="color", rgb=True, color='tan')
            fixed_box._actor = actor
            fixed_box._transform = self.box_transform
            fixed_box._name = "BLOCK"

    def on_pick(self, vtk_picker, event):
        cell_id = vtk_picker.GetCellId()
        mesh = vtk_picker.GetDataSet()
        if cell_id != -1:
            if hasattr(mesh, "_name") and mesh._name == "GRID":
                indices = vtk.vtkIdList()
                mesh.GetCellPoints(cell_id, indices)
                vertices = [mesh.GetPoint(indices.GetId(i)) for i in range(4)]
                center = np.mean(vertices, axis=0)
                self.box_transform = center + box_offset
                box.points = box_points.copy()
                box.translate(self.box_transform)
                plotter.update()
                box_actor.VisibilityOn()
                self.last_pick = "GRID"
            elif hasattr(mesh, "_name") and mesh._name == "BLOCK":
                self.box_transform = mesh._transform
                box.points = box_points.copy()
                box.translate(self.box_transform)
                plotter.update()
                box_actor.VisibilityOn()
                self.last_pick = "BLOCK"
        else:
            box_actor.VisibilityOff()
            self.last_pick = "NONE"


builder = Builder(plotter)
