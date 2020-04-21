import numpy as np
import pyvista as pv
import vtk

# grid
grid_size = 10
grid_length = (grid_size - 1) ** 2
grid = pv.UniformGrid()
grid.dimensions = (grid_size, grid_size, 1)
grid_color = (.7, .7, .7)
grid_scalars = np.tile(grid_color, (grid_length, 1))
grid.cell_arrays["color"] = grid_scalars
grid._name = "GRID"

# box
box = pv.Box(bounds=(0, 1.0, 0, 1.0, 0, 1.0))
box_points = box.points.copy()
box_offset = (-.5, -.5, 0)

# plotter
plotter = pv.BackgroundPlotter(menu_bar=False, toolbar=False)
plotter.enable_anti_aliasing()

plotter.add_mesh(grid, show_edges=True, scalars="color", rgb=True)
box_actor = plotter.add_mesh(box, show_edges=True, color='tan', opacity=0.7)
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
            fixed_box.translate(self.box_transform)
            plotter.add_mesh(fixed_box, show_edges=True, color='tan')
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
        else:
            box_actor.VisibilityOff()


builder = Builder(plotter)
