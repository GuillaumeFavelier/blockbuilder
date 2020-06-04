"""Module about the block element."""

import numpy as np
from .params import rcParams
from .element import ElementId
from .utils import get_structured_grid, get_mesh_cell_array


class Block(object):
    """Main block manager."""

    def __init__(self, dimensions, mesh=None):
        """Initialize the block manager."""
        self.actor = None
        self.element_id = ElementId.BLOCK
        self.unit = rcParams["unit"]
        self.origin = np.asarray(rcParams["origin"])
        self.color_array_name = rcParams["block"]["color_array_name"]
        self.color = np.asarray(rcParams["block"]["color"])
        self.edge_color = np.asarray(rcParams["block"]["edge_color"])
        self.merge_policy = rcParams["block"]["merge_policy"]
        # we assume that the input mesh respect the spacing
        self.spacing = np.asarray([self.unit, self.unit, self.unit])

        if mesh is None:
            self.dimensions = np.asarray(dimensions)
            self.number_of_cells = int(np.prod(self.dimensions - 1))
            self.mesh = get_structured_grid(
                dimensions=self.dimensions,
                origin=self.origin,
                spacing=self.spacing,
                array_name=self.color_array_name,
                color=self.color,
            )
            self.remove_all()
        else:
            self.dimensions = np.asarray(mesh.GetDimensions())
            self.number_of_cells = int(mesh.GetNumberOfCells())
            self.mesh = mesh
        self.color_array = get_mesh_cell_array(
            self.mesh,
            self.color_array_name
        )
        self.plotting = {
            "mesh": self.mesh,
            "edge_color": self.edge_color,
            "rgba": True,
        }

    def merge(self, block):
        """Merge the input block properties."""
        color_array = block.color_array
        for cell_id in range(block.number_of_cells):
            if block.mesh.IsCellVisible(cell_id):
                if self.merge_policy == "external" or \
                   (self.merge_policy == "internal" and
                        not self.mesh.IsCellVisible(cell_id)):
                    coords = _cell_to_coords(cell_id, block.dimensions)
                    cell_id = _coords_to_cell(coords, self.dimensions)
                    self.mesh.UnBlankCell(cell_id)
                    color = color_array.GetTuple3(cell_id)
                    self.color_array.SetTuple3(cell_id, *color)
        self.mesh.Modified()

    def add(self, coords):
        """Add the block at the given coords."""
        if isinstance(coords, tuple):
            area = coords
            for x in np.arange(area[0][0], area[1][0] + 1):
                for y in np.arange(area[0][1], area[1][1] + 1):
                    for z in np.arange(area[0][2], area[1][2] + 1):
                        _coords = [x, y, z]
                        cell_id = _coords_to_cell(_coords, self.dimensions)
                        if not self.mesh.IsCellVisible(cell_id):
                            self.mesh.UnBlankCell(cell_id)
                        self.color_array.SetTuple3(
                            cell_id, *self.color)
        else:
            cell_id = _coords_to_cell(coords, self.dimensions)
            if not self.mesh.IsCellVisible(cell_id):
                self.mesh.UnBlankCell(cell_id)
            self.color_array.SetTuple3(
                cell_id, *self.color)
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
                    for z in np.arange(area[0][2], area[1][2] + 1):
                        _coords = [x, y, z]
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

    def toggle_edges(self, value=None):
        """Toggle visibility of the block edges."""
        if value is None:
            self.show_edges = not self.show_edges
        else:
            self.show_edges = value
        prop = self.actor.GetProperty()
        prop.SetEdgeVisibility(self.show_edges)

    def set_color(self, color, is_int=False):
        """Set the current color."""
        if is_int:
            color = color / 255.
        self.color = color


def _coords_to_cell(coords, dimensions):
    coords = np.asarray(coords)
    cell_id = coords[0] + \
        coords[1] * (dimensions[0] - 1) + \
        coords[2] * (dimensions[0] - 1) * (dimensions[1] - 1)
    return int(cell_id)


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


def _resolve_coincident_topology(actor):
    mapper = actor.GetMapper()
    mapper.SetResolveCoincidentTopologyToPolygonOffset()
    mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(+1., +1.)
