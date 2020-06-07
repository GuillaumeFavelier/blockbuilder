"""Module about the grid element."""

from .element import ElementId, Element


class Grid(Element):
    """Grid element of the scene."""

    def __init__(self, params, dimensions):
        """Initialize the Grid."""
        color = params["grid"]["color"]["build"]
        opacity = params["grid"]["opacity"]
        dimensions = [
            dimensions[0],
            dimensions[1],
            1
        ]
        super().__init__(
            params=params,
            element_id=ElementId.GRID,
            dimensions=dimensions,
            color=color,
            opacity=opacity,
        )
