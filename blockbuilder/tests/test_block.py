import numpy as np
import vtk
import pytest
from blockbuilder.utils import _hasattr, get_structured_grid
from blockbuilder.element import ElementId
from blockbuilder.block import Block


@pytest.mark.parametrize('mesh', [
    None,
    get_structured_grid(),
    ])
def test_block(mesh):
    dimensions = [3, 3, 3]
    block = Block(dimensions=dimensions, mesh=mesh)

    assert _hasattr(block, "actor", type(None))
    assert _hasattr(block, "element_id", ElementId)
    assert _hasattr(block, "unit", float)
    assert _hasattr(block, "origin", np.ndarray)
    assert _hasattr(block, "color_array_name", str)
    assert _hasattr(block, "color", np.ndarray)
    assert _hasattr(block, "edge_color", np.ndarray)
    assert _hasattr(block, "merge_policy", str)
    assert _hasattr(block, "spacing", np.ndarray)
    assert _hasattr(block, "dimensions", np.ndarray)
    assert _hasattr(block, "number_of_cells", int)
    assert _hasattr(block, "mesh", vtk.vtkStructuredGrid)
    assert _hasattr(block, "color_array", vtk.vtkDataArray)
    assert _hasattr(block, "plotting", dict)

    plotting = block.plotting

    assert "mesh" in plotting
    assert "edge_color" in plotting
    assert "rgba" in plotting
