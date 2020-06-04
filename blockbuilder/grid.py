"""Module about the grid element."""

from .params import rcParams
from .element import ElementId, Element


class Grid(Element):
    """Grid element of the scene."""

    def __init__(self, dimensions):
        """Initialize the Grid."""
        color = rcParams["grid"]["color"]["build"]
        opacity = rcParams["grid"]["opacity"]
        dimensions = [
            dimensions[0],
            dimensions[1],
            1
        ]
        super().__init__(
            element_id=ElementId.GRID,
            dimensions=dimensions,
            color=color,
            opacity=opacity,
        )
