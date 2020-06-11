"""Module about the plane element."""

import numpy as np
from .element import ElementId, Element


class Plane(Element):
    """Plane element of the scene."""

    def __init__(self, params, dimensions):
        """Initialize the Plane."""
        unit = params["unit"]
        origin = params["origin"] - np.array([0, 0, unit])
        color = params["plane"]["color"]
        opacity = params["plane"]["opacity"]
        spacing = [
            (dimensions[0] - 1) * unit,
            (dimensions[1] - 1) * unit,
            unit,
        ]
        dimensions = [2, 2, 2]
        super().__init__(
            params=params,
            element_id=ElementId.PLANE,
            dimensions=dimensions,
            color=color,
            opacity=opacity,
            origin=origin,
            spacing=spacing,
        )
