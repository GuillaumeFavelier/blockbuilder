import numpy as np
import pyvista as pv

from .params import rcParams


class Block(object):
    def __init__(self, plotter, element_id, dimensions, unit=None, origin=None,
                 color=None, show_edges=None, edge_color=None, opacity=None):
        if unit is None:
            unit = rcParams["unit"]
        if origin is None:
            origin = rcParams["origin"]
        if color is None:
            color = rcParams["block"]["color"]
        if show_edges is None:
            show_edges = rcParams["block"]["show_edges"]
        if edge_color is None:
            edge_color = rcParams["block"]["edge_color"]
        if opacity is None:
            opacity = rcParams["block"]["opacity"]
        self.plotter = plotter
        self.element_id = element_id
        self.dimensions = np.asarray(dimensions)
        self.unit = unit
        self.origin = np.asarray(origin)
        self.color = color
        self.show_edges = show_edges
        self.edge_color = edge_color
        self.opacity = opacity
        self.spacing = [self.unit, self.unit, self.unit]
        self.length = self.dimensions * self.spacing
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)
        self.mesh = pv.UniformGrid(self.dimensions, self.spacing, self.origin)
        self.actor = self.plotter.add_mesh(
            mesh=self.mesh,
            color=self.color,
            show_edges=self.show_edges,
            edge_color=self.edge_color,
            line_width=rcParams["graphics"]["line_width"],
            opacity=self.opacity,
            reset_camera=False,
        )
        # add data for picking
        self.actor._metadata = self

    def translate(self, tr, update_camera=False):
        # update origin
        self.origin += tr
        self.mesh.SetOrigin(self.origin)

        # update center
        self.center = self.origin + np.multiply(self.dimensions / 2.,
                                                self.spacing)

        if update_camera:
            position = np.array(self.plotter.camera.GetPosition())
            self.plotter.camera.SetPosition(position + tr)
            self.plotter.camera.SetFocalPoint(self.center)
            self.plotter.render()


class Selector(Block):
    def __init__(self, plotter, element_id, unit=None, origin=None, color=None,
                 show_edges=None, edge_color=None, opacity=None):
        if color is None:
            color = rcParams["selector"]["color"]
        if edge_color is None:
            edge_color = rcParams["selector"]["edge_color"]
        if opacity is None:
            opacity = rcParams["selector"]["opacity"]
        dimensions = [2, 2, 2]
        super().__init__(
            plotter=plotter,
            element_id=element_id,
            dimensions=dimensions,
            unit=unit,
            origin=origin,
            color=color,
            edge_color=edge_color,
            opacity=opacity,
        )


class Grid(Block):
    def __init__(self, plotter, element_id, dimensions, unit=None, origin=None,
                 color=None, show_edges=None, edge_color=None, opacity=None):
        if color is None:
            color = rcParams["grid"]["color"]
        if edge_color is None:
            edge_color = rcParams["grid"]["edge_color"]
        if opacity is None:
            opacity = rcParams["grid"]["opacity"]
        super().__init__(
            plotter=plotter,
            element_id=element_id,
            dimensions=dimensions,
            unit=unit,
            origin=origin,
            color=color,
            show_edges=show_edges,
            edge_color=edge_color,
            opacity=opacity,
        )


class Plane(Grid):
    def __init__(self, plotter, element_id, dimensions, unit=None, origin=None,
                 color=None, show_edges=None):
        if color is None:
            color = rcParams["plane"]["color"]
        if show_edges is None:
            show_edges = rcParams["plane"]["show_edges"]
        super().__init__(
            plotter=plotter,
            element_id=element_id,
            dimensions=dimensions,
            unit=unit,
            origin=origin,
            color=color,
            show_edges=show_edges,
        )
