import numpy as np
import vtk
from blockbuilder.params import rcParams
from blockbuilder.utils import _hasattr, get_structured_grid
from blockbuilder.element import ElementId
from blockbuilder.block import Block


def test_block():
    dimensions = [3, 3, 3]
    mesh = get_structured_grid(dimensions=dimensions)
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

    merge_policies = rcParams["block"]["merge_policies"]
    for policy in merge_policies:
        for visible in [False, True]:
            external_block = Block(dimensions=[2, 2, 2])
            if visible:
                external_block.add_all()
            else:
                external_block.remove_all()
            block.merge_policy = policy
            block.merge(external_block)
    assert all(block.dimensions == dimensions)

    block.remove_all()
    assert not block.mesh.IsCellVisible(0)
    block.add(coords=[0, 0, 0])
    block.add(coords=[0, 0, 0])
    assert block.mesh.IsCellVisible(0)
    block.remove(coords=[0, 0, 0])
    block.remove(coords=[0, 0, 0])
    assert not block.mesh.IsCellVisible(0)
    block.add(coords=([0, 0, 0], [0, 0, 1]))
    block.add(coords=([0, 0, 0], [0, 0, 1]))
    assert block.mesh.IsCellVisible(0)
    block.remove(coords=([0, 0, 0], [0, 0, 1]))
    block.remove(coords=([0, 0, 0], [0, 0, 1]))
    assert not block.mesh.IsCellVisible(0)

    block.set_color(color=(255, 255, 255), is_int=True)
    assert np.allclose(block.color, (1., 1., 1.))

    # require an actor (i.e. a plotter)
    # block.toggle_edges(False)
