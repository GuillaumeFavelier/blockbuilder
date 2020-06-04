"""Module about the main application."""

import numpy as np
from .element import ElementId


class Intersection(object):
    """Manage the intersections."""

    def __init__(self, picker):
        """Initialize the Intersection manager."""
        self.any_intersection = (picker.GetCellId() != -1)
        if self.any_intersection:
            self.intersections = [None for element in ElementId]
            self.picked_points = picker.GetPickedPositions()
            self.picked_actors = picker.GetActors()
            for idx, actor in enumerate(self.picked_actors):
                self.intersections[actor.element_id.value] = idx

    def exist(self):
        """Return True if there is any intersection."""
        return self.any_intersection

    def element(self, element_id):
        """Return True if there is any intersection with element_id."""
        return self.intersections[element_id.value] is not None

    def point(self, element_id):
        """Return the intersection point of element_id."""
        idx = self.intersections[element_id.value]
        return np.asarray(self.picked_points.GetPoint(idx))
