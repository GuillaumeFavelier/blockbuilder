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

# plotter
plotter = pv.BackgroundPlotter(menu_bar=False, toolbar=False)


def on_pick(vtk_picker, event):
    cell_id = vtk_picker.GetCellId()
    if cell_id != -1:
        grid_scalars = np.tile(grid_color, (grid_length, 1))
        grid_scalars[cell_id] = (.5, .5, .5)
        grid.cell_arrays["color"] = grid_scalars
        plotter.update_scalars("color")


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

plotter.add_mesh(grid, show_edges=True, scalars="color", rgb=True)
