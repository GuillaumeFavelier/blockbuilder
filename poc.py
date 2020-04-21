import numpy as np
import pyvista as pv
import vtk

# grid
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
plotter.enable_anti_aliasing()

plotter.add_mesh(grid, style="wireframe", color="black")
box_actor = plotter.add_mesh(box, show_edges=True, scalars="color",
                             rgb=True, opacity=0.7)
box_actor.VisibilityOff()


class Builder(object):
    def __init__(self, plotter):
        self.plotter = plotter
        self.button_pressed = False
        self.box_transform = (0, 0, 0)

        iren = self.plotter.iren
        iren.AddObserver(
            vtk.vtkCommand.MouseMoveEvent,
            self.on_mouse_move
        )
        iren.AddObserver(
            vtk.vtkCommand.LeftButtonPressEvent,
            self.on_button_press
        )
        iren.AddObserver(
            vtk.vtkCommand.EndInteractionEvent,
            self.on_button_release
        )

        self.picker = vtk.vtkCellPicker()
        self.picker.AddObserver(
            vtk.vtkCommand.EndPickEvent,
            self.on_pick
        )

    def on_mouse_move(self, vtk_picker, event):
        x, y = vtk_picker.GetEventPosition()
        self.picker.Pick(x, y, 0, plotter.renderer)

    def on_button_press(self, vtk_picker, event):
        self.button_pressed = True

    def on_button_release(self, vtk_picker, event):
        if self.button_pressed:
            fixed_box = pv.Box(bounds=(0, 1.0, 0, 1.0, 0, 1.0))
            fixed_box_color = (1., 1., 1.)
            fixed_box_scalars = np.tile(fixed_box_color, (6, 1))
            fixed_box.cell_arrays["color"] = fixed_box_scalars
            fixed_box.translate(self.box_transform)
            actor = plotter.add_mesh(fixed_box, show_edges=True,
                                     scalars="color", rgb=True, color='tan')
            fixed_box._actor = actor
            fixed_box._transform = self.box_transform
            fixed_box._name = "BLOCK"
        self.button_pressed = False

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
            elif hasattr(mesh, "_name") and mesh._name == "BLOCK":
                self.box_transform = mesh._transform
                box.points = box_points.copy()
                box.translate(self.box_transform)
                plotter.update()
                box_actor.VisibilityOn()
        else:
            box_actor.VisibilityOff()


builder = Builder(plotter)
