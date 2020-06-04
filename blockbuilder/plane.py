"""Module about the plane element."""

import numpy as np
from .params import rcParams
from .element import ElementId, Element


class Plane(Element):
    """Plane element of the scene."""

    def __init__(self, dimensions):
        """Initialize the Plane."""
        unit = rcParams["unit"]
        origin = rcParams["origin"] - np.array([0, 0, unit])
        color = rcParams["plane"]["color"]
        opacity = rcParams["plane"]["opacity"]
        spacing = [
            (dimensions[0] - 1) * unit,
            (dimensions[1] - 1) * unit,
            unit,
        ]
        dimensions = [2, 2, 2]
        super().__init__(
            element_id=ElementId.PLANE,
            dimensions=dimensions,
            color=color,
            opacity=opacity,
            origin=origin,
            spacing=spacing,
        )
