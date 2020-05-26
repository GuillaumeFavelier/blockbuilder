"""Module to describe the elements of the scene."""

import enum
import numpy as np
import vtk

from .params import rcParams


@enum.unique
class Element(enum.Enum):
    """List the different elements of the scene."""

    GRID = 0
    PLANE = 1
    SELECTOR = 2
    BLOCK = 3


@enum.unique
class Symmetry(enum.Enum):
    """List the available kind of symmetry."""

    SYMMETRY_NONE = enum.auto()
    SYMMETRY_X = enum.auto()
    SYMMETRY_Y = enum.auto()
    SYMMETRY_XY = enum.auto()


class Base(object):
    """."""

    def __init__(self, plotter, element_id, dimensions, color,
                 opacity, origin=None, spacing=None):
        """Initialize the Base."""
        self.unit = rcParams["unit"]
        self.edge_color_offset = rcParams["base"]["edge_color_offset"]
        if origin is None:
            origin = rcParams["origin"]
        if spacing is None:
            spacing = [self.unit, self.unit, self.unit]
        self.plotter = plotter
        self.dimensions = np.asarray(dimensions)
        self.origin = np.asarray(origin)
        self.color = color
        self.edge_color = np.asarray(self.color) + self.edge_color_offset
        self.opacity = opacity
        self.spacing = np.asarray(spacing)
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
        self.mesh = vtk.vtkUniformGrid()
        self.mesh.SetDimensions(self.dimensions)
        self.mesh.SetSpacing(self.spacing)
        self.mesh.SetOrigin(self.origin)
        self.actor = self.plotter.add_mesh(
            mesh=self.mesh,
            color=self.color,
            edge_color=self.edge_color,
            opacity=self.opacity,
            reset_camera=False,
        )
        # add data for picking
        self.actor.element_id = element_id

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


class Grid(Base):
    """Grid element of the scene."""

    def __init__(self, plotter, dimensions):
        """Initialize the Grid."""
        color = rcParams["grid"]["color"]["build"]
        opacity = rcParams["grid"]["opacity"]
        dimensions = [
            dimensions[0],
            dimensions[1],
            1
        ]
        super().__init__(
            plotter=plotter,
            element_id=Element.GRID,
            dimensions=dimensions,
            color=color,
            opacity=opacity,
        )


class Plane(Base):
    """Plane element of the scene."""

    def __init__(self, plotter, dimensions):
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
            plotter=plotter,
            element_id=Element.PLANE,
            dimensions=dimensions,
            color=color,
            opacity=opacity,
            origin=origin,
            spacing=spacing,
        )
        mapper = self.actor.GetMapper()
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(+1., +1.)


class Selector(Base):
    """Selector element of the scene."""

    def __init__(self, plotter):
        """Initialize the Selector."""
        dimensions = [2, 2, 2]
        color = rcParams["selector"]["color"]["build"]
        opacity = rcParams["selector"]["opacity"]
        super().__init__(
            plotter=plotter,
            element_id=Element.SELECTOR,
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

    def __init__(self, plotter):
        """Initialize the selector."""
        super().__init__(plotter)
        self.area = None

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

    def selection_area(self):
        """Return the current area selection."""
        return self.area


class SymmetrySelector(AreaSelector):
    """Selector that supports symmetry."""

    def __init__(self, plotter, dimensions):
        """Initialize the selector."""
        super().__init__(plotter)
        self.selector_x = AreaSelector(plotter)
        self.selector_y = AreaSelector(plotter)
        self.selector_xy = AreaSelector(plotter)
        self.symmetry = Symmetry.SYMMETRY_NONE
        self.dimensions = dimensions

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


class Block(object):
    """Main block manager."""

    def __init__(self, plotter, dimensions):
        """Initialize the block manager."""
        self.unit = rcParams["unit"]
        self.origin = rcParams["origin"]
        self.color_array = rcParams["block"]["color_array"]
        self.color = rcParams["block"]["color"]
        self.edge_color = rcParams["block"]["edge_color"]
        self.plotter = plotter
        self.dimensions = np.asarray(dimensions)
        self.spacing = np.asarray([self.unit, self.unit, self.unit])

        counter = 0
        self.number_of_points = np.prod(self.dimensions)
        self.number_of_cells = np.prod(self.dimensions - 1)
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(self.number_of_points)
        for k in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                for i in range(self.dimensions[2]):
                    point = self.origin + np.multiply([i, j, k], self.spacing)
                    points.SetPoint(counter, point)
                    counter += 1

        self.mesh = vtk.vtkStructuredGrid()
        self.mesh.SetDimensions(self.dimensions)
        self.mesh.SetPoints(points)
        _set_mesh_cell_array(
            self.mesh,
            self.color_array,
            np.tile(self.color, (self.number_of_cells, 1)),
        )
        self.remove_all()
        actor = self.plotter.add_mesh(
            self.mesh,
            scalars=self.color_array,
            rgba=True,
            show_scalar_bar=False,
            edge_color=self.edge_color,
            reset_camera=False,
        )
        actor.element_id = Element.BLOCK

    def add(self, coords):
        """Add the block at the given coords."""
        if isinstance(coords, tuple):
            area = coords
            for x in np.arange(area[0][0], area[1][0] + 1):
                for y in np.arange(area[0][1], area[1][1] + 1):
                    _coords = [x, y, area[0][2]]
                    cell_id = _coords_to_cell(_coords, self.dimensions)
                    if not self.mesh.IsCellVisible(cell_id):
                        self.mesh.UnBlankCell(cell_id)
        else:
            cell_id = _coords_to_cell(coords, self.dimensions)
            if not self.mesh.IsCellVisible(cell_id):
                self.mesh.UnBlankCell(cell_id)
        self.mesh.Modified()

    def add_all(self):
        """Add all the blocks."""
        for cell_id in range(self.number_of_cells):
            self.mesh.UnBlankCell(cell_id)
        self.mesh.Modified()

    def remove(self, coords):
        """Remove the block at the given coords."""
        if isinstance(coords, tuple):
            area = coords
            for x in np.arange(area[0][0], area[1][0] + 1):
                for y in np.arange(area[0][1], area[1][1] + 1):
                    _coords = [x, y, area[0][2]]
                    cell_id = _coords_to_cell(_coords, self.dimensions)
                    if self.mesh.IsCellVisible(cell_id):
                        self.mesh.BlankCell(cell_id)
                        self.mesh.Modified()
        else:
            cell_id = _coords_to_cell(coords, self.dimensions)
            if self.mesh.IsCellVisible(cell_id):
                self.mesh.BlankCell(cell_id)
                self.mesh.Modified()

    def remove_all(self):
        """Remove all the blocks."""
        for cell_id in range(self.number_of_cells):
            self.mesh.BlankCell(cell_id)
        self.mesh.Modified()


def _coords_to_cell(coords, dimensions):
    coords = np.asarray(coords)
    cell_id = coords[0] + \
        coords[1] * (dimensions[0] - 1) + \
        coords[2] * (dimensions[0] - 1) * (dimensions[1] - 1)
    return cell_id


def _cell_to_coords(cell_id, dimensions):
    offset = [
        0,
        (dimensions[0] - 1),
        (dimensions[0] - 1) * (dimensions[1] - 1),
    ]
    coords = np.empty(3)
    coords[2] = np.floor(cell_id / offset[2])
    coords[1] = cell_id % offset[2]
    coords[1] = np.floor(coords[1] / offset[1])
    coords[0] = (cell_id % offset[2]) % offset[1]
    return coords


def _set_mesh_cell_array(mesh, array_name, array):
    from vtk.util.numpy_support import numpy_to_vtk
    cell_data = mesh.GetCellData()
    vtk_array = numpy_to_vtk(array)
    vtk_array.SetName(array_name)
    cell_data.AddArray(vtk_array)
    cell_data.SetActiveScalars(array_name)
