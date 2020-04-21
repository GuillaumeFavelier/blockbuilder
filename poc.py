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


def on_pick(vtk_picker, event):
    cell_id = vtk_picker.GetCellId()
    mesh = vtk_picker.GetDataSet()
    if cell_id != -1:
        if hasattr(mesh, "_name") and mesh._name == "GRID":
            indices = vtk.vtkIdList()
            mesh.GetCellPoints(cell_id, indices)
            vertices = [mesh.GetPoint(indices.GetId(i)) for i in range(4)]
            center = np.mean(vertices, axis=0)
            box.points = box_points.copy() + box_offset
            box.translate(center)
            plotter.update()
            box_actor.VisibilityOn()
    else:
        box_actor.VisibilityOff()


picker = vtk.vtkCellPicker()
picker.AddObserver(
    vtk.vtkCommand.EndPickEvent,
    on_pick
)


def on_mouse_move(vtk_picker, event):
    x, y = vtk_picker.GetEventPosition()
    picker.Pick(x, y, 0, plotter.renderer)


iren = plotter.iren
iren.AddObserver(
    vtk.vtkCommand.MouseMoveEvent,
    on_mouse_move
)
