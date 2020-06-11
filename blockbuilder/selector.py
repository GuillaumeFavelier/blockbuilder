"""Module about the selector element."""

import enum
import numpy as np
from .element import ElementId, Element


@enum.unique
class Symmetry(enum.Enum):
    """List the available kind of symmetry."""

    SYMMETRY_NONE = enum.auto()
    SYMMETRY_X = enum.auto()
    SYMMETRY_Y = enum.auto()
    SYMMETRY_XY = enum.auto()


class Selector(Element):
    """Selector element of the scene."""

    def __init__(self, params):
        """Initialize the Selector."""
        dimensions = [2, 2, 2]
        color = params["selector"]["color"]["build"]
        opacity = params["selector"]["opacity"]
        super().__init__(
            params=params,
            element_id=ElementId.SELECTOR,
            dimensions=dimensions,
            color=color,
            opacity=opacity,
        )
        self.coords = None
        self.coords_type = np.int

    def select(self, coords):
        """Select a block of the grid."""
        self.coords = coords.astype(self.coords_type)
        origin = coords * self.unit
        self.mesh.SetOrigin(origin)

    def show(self):
        """Show the selector."""
        self.actor.VisibilityOn()

    def hide(self):
        """Hide the selector."""
        self.actor.VisibilityOff()

    def selection(self):
        """Return the current selection."""
        return self.coords


class AreaSelector(Selector):
    """Selector that supports area."""

    def __init__(self, params):
        """Initialize the selector."""
        super().__init__(params=params)
        self.area = None
        self.area_first_coords = None
        self.area_last_coords = None

    def select_area(self, area):
        """Select the area."""
        area = np.asarray(area).astype(self.coords_type)
        self.area = (
            np.min(area, axis=0),
            np.max(area, axis=0),
        )
        coords_diff = self.area[1] - self.area[0] + 2
        self.select(self.area[0])
        self.mesh.SetDimensions(coords_diff)
        self.mesh.Modified()

    def reset_area(self):
        """Reset the selector."""
        dimensions = [2, 2, 2]
        self.mesh.SetDimensions(dimensions)
        self.mesh.Modified()
        self.area_first_coords = None
        self.area_last_coords = None

    def get_first_coords(self):
        """Get the first coordinates of the selection area."""
        return self.area_first_coords

    def get_last_coords(self):
        """Get the last coordinates of the selection area."""
        return self.area_last_coords

    def set_first_coords(self, coords):
        """Set the first coordinates of the selection area."""
        self.area_first_coords = coords

    def set_last_coords(self, coords):
        """Set the last coordinates of the selection area."""
        self.area_last_coords = coords

    def selection_area(self):
        """Return the current area selection."""
        return self.area


class SymmetrySelector(AreaSelector):
    """Selector that supports symmetry."""

    def __init__(self, params, dimensions):
        """Initialize the selector."""
        super().__init__(params=params)
        self.selector_x = AreaSelector(params=params)
        self.selector_y = AreaSelector(params=params)
        self.selector_xy = AreaSelector(params=params)
        self.symmetry = Symmetry.SYMMETRY_NONE
        self.dimensions = np.asarray(dimensions)

    def set_block_mode(self, mode):
        """Set the block mode."""
        super().set_block_mode(mode)
        self.selector_x.set_block_mode(mode)
        self.selector_y.set_block_mode(mode)
        self.selector_xy.set_block_mode(mode)

    def select_area(self, area):
        """Select the area."""
        super().select_area(area)
        area = np.asarray(area).astype(self.coords_type)
        if self.symmetry in (Symmetry.SYMMETRY_X, Symmetry.SYMMETRY_XY):
            new_area = area.copy()
            new_area[0][1] = self.dimensions[1] - area[0][1] - 2
            new_area[1][1] = self.dimensions[1] - area[1][1] - 2
            self.selector_x.select_area(new_area)
        if self.symmetry in (Symmetry.SYMMETRY_Y, Symmetry.SYMMETRY_XY):
            new_area = area.copy()
            new_area[0][0] = self.dimensions[0] - area[0][0] - 2
            new_area[1][0] = self.dimensions[0] - area[1][0] - 2
            self.selector_y.select_area(new_area)
        if self.symmetry is Symmetry.SYMMETRY_XY:
            new_area[0][1] = self.dimensions[1] - area[0][1] - 2
            new_area[1][1] = self.dimensions[1] - area[1][1] - 2
            new_area[0][0] = self.dimensions[0] - area[0][0] - 2
            new_area[1][0] = self.dimensions[0] - area[1][0] - 2
            self.selector_xy.select_area(new_area)

    def reset_area(self):
        """Reset the selector."""
        super().reset_area()
        self.selector_x.reset_area()
        self.selector_y.reset_area()
        self.selector_xy.reset_area()

    def select(self, coords):
        """Select a block of the grid."""
        super().select(coords)
        if self.symmetry in (Symmetry.SYMMETRY_X, Symmetry.SYMMETRY_XY):
            new_coords = coords.copy()
            new_coords[1] = self.dimensions[1] - coords[1] - 2
            self.selector_x.select(new_coords)
        if self.symmetry in (Symmetry.SYMMETRY_Y, Symmetry.SYMMETRY_XY):
            new_coords = coords.copy()
            new_coords[0] = self.dimensions[0] - coords[0] - 2
            self.selector_y.select(new_coords)
        if self.symmetry is Symmetry.SYMMETRY_XY:
            new_coords = coords.copy()
            new_coords[1] = self.dimensions[1] - coords[1] - 2
            new_coords[0] = self.dimensions[0] - coords[0] - 2
            self.selector_xy.select(new_coords)

    def show(self):
        """Show the selector."""
        super().show()
        if self.symmetry in (Symmetry.SYMMETRY_X, Symmetry.SYMMETRY_XY):
            self.selector_x.actor.VisibilityOn()
        if self.symmetry in (Symmetry.SYMMETRY_Y, Symmetry.SYMMETRY_XY):
            self.selector_y.actor.VisibilityOn()
        if self.symmetry is Symmetry.SYMMETRY_XY:
            self.selector_xy.actor.VisibilityOn()

    def hide(self):
        """Hide the selector."""
        super().hide()
        self.selector_x.actor.VisibilityOff()
        self.selector_y.actor.VisibilityOff()
        self.selector_xy.actor.VisibilityOff()

    def selection(self):
        """Return the current selection."""
        coords = [self.coords]
        if self.symmetry in (Symmetry.SYMMETRY_X, Symmetry.SYMMETRY_XY):
            coords.append(self.selector_x.coords)
        if self.symmetry in (Symmetry.SYMMETRY_Y, Symmetry.SYMMETRY_XY):
            coords.append(self.selector_y.coords)
        if self.symmetry is Symmetry.SYMMETRY_XY:
            coords.append(self.selector_xy.coords)
        return coords

    def selection_area(self):
        """Return the current area selection."""
        area = [self.area]
        if self.symmetry in (Symmetry.SYMMETRY_X, Symmetry.SYMMETRY_XY):
            area.append(self.selector_x.area)
        if self.symmetry in (Symmetry.SYMMETRY_Y, Symmetry.SYMMETRY_XY):
            area.append(self.selector_y.area)
        if self.symmetry is Symmetry.SYMMETRY_XY:
            area.append(self.selector_xy.area)
        return area

    def set_symmetry(self, value):
        """Set the symmetry."""
        self.symmetry = value
