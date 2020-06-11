"""Module to describe the elements of the scene."""

import enum
import numpy as np
import vtk


@enum.unique
class ElementId(enum.Enum):
    """List the different elements of the scene."""

    GRID = 0
    PLANE = 1
    SELECTOR = 2
    BLOCK = 3


class Element(object):
    """Base element."""

    def __init__(self, params, element_id, dimensions, color,
                 opacity, origin=None, spacing=None):
        """Initialize the Element."""
        self.actor = None
        self.params = params
        self.element_id = element_id
        self.unit = self.params["unit"]
        self.edge_color_offset = self.params["element"]["edge_color_offset"]
        if origin is None:
            origin = self.params["origin"]
        if spacing is None:
            spacing = [self.unit, self.unit, self.unit]
        self.dimensions = np.asarray(dimensions)
        self.origin = np.asarray(origin)
        self.spacing = np.asarray(spacing)
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
        self.color = np.asarray(color)
        self.edge_color = np.asarray(self.color) + self.edge_color_offset
        self.opacity = float(opacity)
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
        if self.actor is None:
            raise ValueError("Element's actor is not initialized.")
        else:
            element_name = self.actor.element_id.name.lower()
            mode_name = mode.name.lower()
            self.color = self.params[element_name]["color"][mode_name]
            self.edge_color = np.asarray(self.color) + self.edge_color_offset
            # update colors
            prop = self.actor.GetProperty()
            prop.SetColor(self.color)
            prop.SetEdgeColor(self.edge_color)

    def translate(self, tr):
        """Translate the Base."""
        # update origin
        self.origin += np.asarray(tr)
        self.mesh.SetOrigin(self.origin)

        # update center
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
