import enum
import numpy as np
import pyvista as pv
import vtk

from .params import rcParams


@enum.unique
class Element(enum.Enum):
    GRID = 0
    PLANE = 1
    SELECTOR = 2
    BLOCK = 3


class Grid(object):
    def __init__(self, plotter, dimensions, origin=None, color=None,
                 show_edges=None, edge_color=None, opacity=None):
        self.unit = rcParams["unit"]
        self.color_array = rcParams["block"]["color_array"]
        if origin is None:
            origin = rcParams["origin"]
        if color is None:
            color = rcParams["grid"]["color"]["build"]
        if show_edges is None:
            show_edges = rcParams["grid"]["show_edges"]
        if opacity is None:
            opacity = rcParams["grid"]["opacity"]
        self.plotter = plotter
        self.dimensions = np.asarray(dimensions)
        self.origin = np.asarray(origin)
        self.color = color
        self.show_edges = show_edges
        self.edge_color = self.color + np.array([.15, .15, .15])
        self.opacity = opacity
        self.spacing = [self.unit, self.unit, self.unit]
        self.length = self.dimensions * self.spacing
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
        self.mesh = pv.UniformGrid(self.dimensions, self.spacing, self.origin)
        self.actor = self.plotter.add_mesh(
            mesh=self.mesh,
            color=self.color,
            show_scalar_bar=False,
            show_edges=self.show_edges,
            edge_color=self.edge_color,
            line_width=rcParams["graphics"]["line_width"],
            opacity=self.opacity,
            reset_camera=False,
        )
        # add data for picking
        self.actor.element_id = Element.GRID

    def set_block_mode(self, mode):
        element_name = self.actor.element_id.name.lower()
        mode_name = mode.name.lower()
        self.color = rcParams[element_name]["color"][mode_name]
        self.edge_color = self.color + np.array([.15, .15, .15])
        # update colors
        prop = self.actor.GetProperty()
        prop.SetColor(self.color)
        prop.SetEdgeColor(self.edge_color)

    def translate(self, tr, update_camera=False):
        # update origin
        self.origin += tr
        self.mesh.SetOrigin(self.origin)

        # update center
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)


class Plane(Grid):
    def __init__(self, plotter, dimensions, color=None, show_edges=None):
        unit = rcParams["unit"]
        origin = rcParams["origin"] - np.array([0, 0, unit])
        opacity = rcParams["plane"]["opacity"]
        if color is None:
            color = rcParams["plane"]["color"]
        if show_edges is None:
            show_edges = rcParams["plane"]["show_edges"]
        super().__init__(
            plotter=plotter,
            dimensions=dimensions,
            origin=origin,
            color=color,
            show_edges=show_edges,
            opacity=opacity,
        )
        # add data for picking
        self.actor.element_id = Element.PLANE


class Selector(Grid):
    def __init__(self, plotter, color=None):
        dimensions = rcParams["selector"]["dimensions"]
        super().__init__(
            plotter=plotter,
            color=color,
            dimensions=dimensions,
        )
        # add data for picking
        self.actor.element_id = Element.SELECTOR

    def select(self, coords):
        origin = coords * self.unit
        self.mesh.SetOrigin(origin)

    def show(self):
        self.actor.VisibilityOn()

    def hide(self):
        self.actor.VisibilityOff()


class Block(object):
    def __init__(self, plotter, dimensions, color=None, edge_color=None):
        self.show_edges = rcParams["block"]["show_edges"]
        self.color_array = rcParams["block"]["color_array"]
        if color is None:
            color = rcParams["block"]["color"]
        if edge_color is None:
            edge_color = rcParams["block"]["edge_color"]
        self.plotter = plotter
        self.dimensions = np.asarray(dimensions)
        self.color = color
        self.edge_color = edge_color

        counter = 0
        self.number_of_points = np.prod(self.dimensions)
        self.number_of_cells = np.prod(self.dimensions - 1)
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(self.number_of_points)
        for k in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                for i in range(self.dimensions[2]):
                    points.SetPoint(counter, i, j, k)
                    counter += 1

        self.mesh = pv.StructuredGrid()
        self.mesh.SetDimensions(self.dimensions)
        self.mesh.SetPoints(points)
        self.mesh.cell_arrays[self.color_array] = np.tile(
           self.color,
           (self.number_of_cells, 1),
        )
        self.remove_all()
        actor = self.plotter.add_mesh(
            self.mesh,
            scalars=self.color_array,
            rgb=True,
            show_scalar_bar=False,
            show_edges=self.show_edges,
            edge_color=self.edge_color,
            line_width=rcParams["graphics"]["line_width"],
            reset_camera=False,
        )
        actor.element_id = Element.BLOCK

    def add(self, coords):
        cell_id = _coords_to_cell(coords, self.dimensions)
        if not self.mesh.IsCellVisible(cell_id):
            self.mesh.UnBlankCell(cell_id)
            self.mesh.Modified()

    def add_all(self):
        for cell_id in range(self.number_of_cells):
            self.mesh.UnBlankCell(cell_id)

    def remove(self, coords):
        cell_id = _coords_to_cell(coords, self.dimensions)
        if self.mesh.IsCellVisible(cell_id):
            self.mesh.BlankCell(cell_id)
            self.mesh.Modified()

    def remove_all(self):
        for cell_id in range(self.number_of_cells):
            self.mesh.BlankCell(cell_id)


def _coords_to_cell(coords, dimensions):
    coords = np.asarray(coords)
    cell_id = coords[0] + \
        coords[1] * (dimensions[0] - 1) + \
        coords[2] * (dimensions[0] - 1) * (dimensions[1] - 1)
    return cell_id
