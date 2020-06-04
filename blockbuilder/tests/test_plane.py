import numpy as np
from blockbuilder.element import ElementId
from blockbuilder.plane import Plane


def test_plane():
    dimensions = [3, 3, 3]
    plane = Plane(dimensions=dimensions)

    assert plane.element_id == ElementId.PLANE
    assert np.allclose(plane.dimensions, [2, 2, 2])
