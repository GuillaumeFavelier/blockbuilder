import numpy as np
import vtk
import pytest
from blockbuilder.utils import _hasattr
from blockbuilder.element import ElementId, Element


def test_element():
    value = np.random.randint(0, len(ElementId))
    element_id = ElementId(value)
    dimensions = [2, 2, 2]
    white = (1., 1., 1.)
    opacity = 1.
    element = Element(
        element_id=element_id,
        dimensions=dimensions,
        color=white,
        opacity=opacity,
    )
    assert _hasattr(element, "actor", type(None))
    assert _hasattr(element, "element_id", ElementId)
    assert _hasattr(element, "unit", float)
    assert _hasattr(element, "edge_color_offset", list)
    assert _hasattr(element, "dimensions", np.ndarray)
    assert _hasattr(element, "origin", np.ndarray)
    assert _hasattr(element, "spacing", np.ndarray)
    assert _hasattr(element, "center", np.ndarray)
    assert _hasattr(element, "color", np.ndarray)
    assert _hasattr(element, "edge_color", np.ndarray)
    assert _hasattr(element, "opacity", float)
    assert _hasattr(element, "mesh", vtk.vtkUniformGrid)
    assert _hasattr(element, "plotting", dict)

    assert element.element_id.value == value
    assert np.allclose(element.color, white)
    assert np.allclose(element.opacity, opacity)

    mesh = element.mesh

    assert np.allclose(mesh.GetDimensions(), dimensions)

    plotting = element.plotting

    assert "mesh" in plotting
    assert "color" in plotting
    assert "edge_color" in plotting
    assert "opacity" in plotting

    with pytest.raises(ValueError, match="actor"):
        element.set_block_mode(None)

    tr = np.asarray([0, 0, 1])
    origin = element.mesh.GetOrigin()
    element.translate(tr)
    assert np.allclose(element.mesh.GetOrigin(), origin + tr)
