"""Module about shared utility features."""

import warnings
from pathlib import Path
import re
import numpy as np
import vtk
from scooby import Report


class DefaultFunction():
    """Function called with its default value."""

    def __init__(self, func, default_value):
        """Initialize the DefaultFunction."""
        self.func = func
        self.default_value = default_value

    def __call__(self, unused=None):
        """Call the DefaultFunction."""
        del unused
        return self.func(self.default_value)


def report():
    """Return the report."""
    def _readline(p):
        with open(p) as f:
            lst = [line.rstrip('\n') for line in f]
        return lst

    def _match(s):
        m = re.search("[a-zA-Z0-9-]*", s)
        return m.group(0)

    def _filter(p):
        return [_match(el) for el in _readline(p)]

    root_path = Path(__file__).parent.parent
    core_path = Path(root_path, "requirements.txt")
    qt_path = Path(root_path, "requirements_qt.txt")
    testing_path = Path(root_path, "requirements_testing.txt")
    core = _filter(core_path)
    additional = _filter(qt_path)
    optional = _filter(testing_path)
    return Report(
        core=core,
        additional=additional,
        optional=optional,
    )


def _hasattr(variable, attribute_name, variable_type):
    if not hasattr(variable, attribute_name):
        return False
    return isinstance(getattr(variable, attribute_name), variable_type)


def add_mesh_cell_array(mesh, array_name, array):
    """Add a cell array to the mesh."""
    from vtk.util.numpy_support import numpy_to_vtk
    cell_data = mesh.GetCellData()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        vtk_array = numpy_to_vtk(array)
    vtk_array.SetName(array_name)
    cell_data.AddArray(vtk_array)
    cell_data.SetActiveScalars(array_name)
    return vtk_array


def get_mesh_cell_array(mesh, array_name):
    """Retrieve a cell array from the mesh."""
    cell_data = mesh.GetCellData()
    return cell_data.GetArray(array_name)


def get_poly_data():
    """Create a vtkPolyData."""
    mesh = vtk.vtkSphereSource()
    mesh.SetPhiResolution(8)
    mesh.SetThetaResolution(8)
    return mesh.GetOutput()


def get_uniform_grid(dimensions=(2, 2, 2), origin=(0., 0., 0.),
                     spacing=(1., 1., 1.)):
    """Create a vtkUniformGrid."""
    mesh = vtk.vtkUniformGrid()
    mesh.Initialize()
    mesh.SetDimensions(*dimensions)
    mesh.SetOrigin(*origin)
    mesh.SetSpacing(*spacing)
    return mesh


def get_structured_grid(dimensions=(2, 2, 2), origin=(0., 0., 0.),
                        spacing=(1., 1., 1.), array_name="color",
                        color=(1., 1., 1.)):
    """Create a vtkStructuredGrid."""
    dimensions = np.asarray(dimensions)
    mesh = vtk.vtkStructuredGrid()
    mesh.SetDimensions(*dimensions)

    counter = 0
    number_of_points = np.prod(dimensions)
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(number_of_points)
    for k in range(dimensions[2]):
        for j in range(dimensions[1]):
            for i in range(dimensions[0]):
                point = origin + np.multiply([i, j, k], spacing)
                points.SetPoint(counter, point)
                counter += 1
    mesh.SetPoints(points)

    number_of_cells = np.prod(dimensions - 1)
    array = np.tile(color, (number_of_cells, 1))
    add_mesh_cell_array(
        mesh=mesh,
        array_name=array_name,
        array=array,
    )
    mesh.Modified()
    return mesh


def _rgb2str(color, is_int=False):
    if not is_int:
        color = np.asarray(color) * 255
        color = color.astype(np.uint8)
    return str(tuple(color))


def _qrgb2rgb(color):
    return (
        color.red(),
        color.green(),
        color.blue()
    )
