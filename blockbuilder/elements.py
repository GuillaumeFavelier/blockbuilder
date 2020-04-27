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


class Base(object):
    def __init__(self, plotter, element_id, dimensions, color,
                 opacity, origin=None, spacing=None):
        self.unit = rcParams["unit"]
        if origin is None:
            origin = rcParams["origin"]
        if spacing is None:
            spacing = [self.unit, self.unit, self.unit]
        self.plotter = plotter
        self.dimensions = np.asarray(dimensions)
        self.origin = np.asarray(origin)
        self.color = color
        self.edge_color = self.color + np.array([.15, .15, .15])
        self.opacity = opacity
        self.spacing = np.asarray(spacing)
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
        self.mesh = pv.UniformGrid(self.dimensions, self.spacing, self.origin)
        self.actor = self.plotter.add_mesh(
            mesh=self.mesh,
            color=self.color,
            edge_color=self.edge_color,
            show_edges=rcParams["graphics"]["show_edges"],
            line_width=rcParams["graphics"]["line_width"],
            opacity=self.opacity,
            reset_camera=False,
        )
        # add data for picking
        self.actor.element_id = element_id

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


class Grid(Base):
    def __init__(self, plotter, dimensions):
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
    def __init__(self, plotter, dimensions):
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
    def __init__(self, plotter):
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

    def select(self, coords):
        origin = coords * self.unit
        self.mesh.SetOrigin(origin)

    def show(self):
        self.actor.VisibilityOn()

    def hide(self):
        self.actor.VisibilityOff()


class Block(object):
    def __init__(self, plotter, dimensions):
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
            rgba=True,
            show_scalar_bar=False,
            edge_color=self.edge_color,
            show_edges=rcParams["graphics"]["show_edges"],
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
        self.mesh.Modified()

    def remove(self, coords):
        cell_id = _coords_to_cell(coords, self.dimensions)
        if self.mesh.IsCellVisible(cell_id):
            self.mesh.BlankCell(cell_id)
            self.mesh.Modified()

    def remove_all(self):
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
    coords = np.empty(3)
    coords[2] = np.floor(cell_id / ((dimensions[0] - 1) * (dimensions[1] - 1)))
    coords[1] = cell_id % ((dimensions[0] - 1) * (dimensions[1] - 1))
    coords[1] = np.floor(coords[1] / dimensions[0] - 1)
    coords[0] = (cell_id % ((dimensions[0] - 1) * (dimensions[1] - 1))) % (dimensions[0] - 1)
    return coords
