"""Module to describe the elements of the scene."""

import enum
import numpy as np
import vtk
from .params import rcParams


@enum.unique
class ElementId(enum.Enum):
    """List the different elements of the scene."""

    GRID = 0
    PLANE = 1
    SELECTOR = 2
    BLOCK = 3


class Element(object):
    """Base element."""

    def __init__(self, element_id, dimensions, color,
                 opacity, origin=None, spacing=None):
        """Initialize the Element."""
        self.actor = None
        self.element_id = element_id
        self.unit = rcParams["unit"]
        self.edge_color_offset = rcParams["base"]["edge_color_offset"]
        if origin is None:
            origin = rcParams["origin"]
        if spacing is None:
            spacing = [self.unit, self.unit, self.unit]
        self.dimensions = np.asarray(dimensions)
        self.origin = np.asarray(origin)
        self.color = color
        self.edge_color = np.asarray(self.color) + self.edge_color_offset
        self.opacity = opacity
        self.spacing = np.asarray(spacing)
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
        self.mesh = vtk.vtkUniformGrid()
        self.mesh.Initialize()
        self.mesh.SetDimensions(self.dimensions)
        self.mesh.SetSpacing(self.spacing)
        self.mesh.SetOrigin(self.origin)
        self.plotting = {
            "mesh": self.mesh,
            "color": self.color,
            "edge_color": self.edge_color,
            "opacity": self.opacity,
        }

    def set_block_mode(self, mode):
        """Set the block mode."""
        element_name = self.actor.element_id.name.lower()
        mode_name = mode.name.lower()
        self.color = rcParams[element_name]["color"][mode_name]
        self.edge_color = np.asarray(self.color) + self.edge_color_offset
        # update colors
        prop = self.actor.GetProperty()
        prop.SetColor(self.color)
        prop.SetEdgeColor(self.edge_color)

    def translate(self, tr, update_camera=False):
        """Translate the Base."""
        # update origin
        self.origin += tr
        self.mesh.SetOrigin(self.origin)

        # update center
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
