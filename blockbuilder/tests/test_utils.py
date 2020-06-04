import vtk
from blockbuilder.utils import (_hasattr, get_poly_data, get_uniform_grid,
                                get_structured_grid, get_mesh_cell_array)


def test_hasattr():
    class A():
        def __init__(self):
            self.a = True

    variable = A()
    assert _hasattr(variable, "a", bool)
    assert not _hasattr(variable, "b", bool)

    poly_data = get_poly_data()
    assert isinstance(poly_data, vtk.vtkPolyData)

    uniform_grid = get_uniform_grid()
    assert isinstance(uniform_grid, vtk.vtkUniformGrid)

    structured_grid = get_structured_grid()
    assert isinstance(structured_grid, vtk.vtkStructuredGrid)

    array = get_mesh_cell_array(structured_grid, "color")
    assert isinstance(array, vtk.vtkDataArray)
