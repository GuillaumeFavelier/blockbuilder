import numpy as np

from blockbuilder.params import rcParams
from blockbuilder.element import ElementId
from blockbuilder.plane import Plane


def test_plane():
    dimensions = [3, 3, 3]
    plane = Plane(params=rcParams, dimensions=dimensions)

    assert plane.element_id == ElementId.PLANE
    assert np.allclose(plane.dimensions, [2, 2, 2])
