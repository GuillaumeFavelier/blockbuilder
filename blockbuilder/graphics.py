"""Module about visual properties."""

import numpy as np
import pyvista as pv

from .params import rcParams


class Graphics(object):
    """Manage the visual properties."""

    def __init__(self, window_size=None, line_width=None, advanced=None,
                 show_fps=None, background_top_color=None,
                 background_bottom_color=None):
        """Initialize the default visual properties."""
        if window_size is None:
            window_size = rcParams["graphics"]["window_size"]
        if line_width is None:
            line_width = rcParams["graphics"]["line_width"]
        if advanced is None:
            advanced = rcParams["graphics"]["advanced"]
        if show_fps is None:
            show_fps = rcParams["graphics"]["show_fps"]
        if background_top_color is None:
            background_top_color = rcParams["graphics"]["background_top_color"]
        if background_bottom_color is None:
            background_bottom_color = \
                rcParams["graphics"]["background_bottom_color"]
        self.window_size = window_size
        self.line_width = line_width
        self.advanced = advanced
        self.show_fps = show_fps
        self.background_top_color = background_top_color
        self.background_bottom_color = background_bottom_color
        self.pyvista_menu_bar = rcParams["graphics"]["pyvista_menu_bar"]
        self.pyvista_toolbar = rcParams["graphics"]["pyvista_toolbar"]
        self.fps_position = rcParams["graphics"]["fps_position"]
        self.font_size = rcParams["graphics"]["font_size"]
        self.plotter = None
        self.window = None

        # configuration
        self.load_plotter()
        self.load_graphic_quality()
        self.load_fps()

    def render(self):
        """Render the scene."""
        # fix the clipping planes being too small
        rng = [0] * 6
        self.plotter.renderer.ComputeVisiblePropBounds(rng)
        self.plotter.renderer.ResetCameraClippingRange(rng)
        if hasattr(self.plotter, "ren_win"):
            self.plotter.ren_win.Render()

    def load_plotter(self):
        """Configure the internal plotter."""
        # we disable auto_update to minimize the number of render calls
        self.plotter = pv.BackgroundPlotter(
            window_size=self.window_size,
            menu_bar=self.pyvista_menu_bar,
            toolbar=self.pyvista_toolbar,
            auto_update=0,
        )
        self.window = self.plotter.app_window
        self.plotter.set_background(
            color=self.background_bottom_color,
            top=self.background_top_color,
        )
        self.plotter.show_axes()

    def load_graphic_quality(self):
        """Configure the visual quality."""
        if self.advanced:
            self.plotter.enable_anti_aliasing()
            self.plotter.ren_win.LineSmoothingOn()
            self.plotter.ren_win.PolygonSmoothingOn()
        else:
            self.plotter.disable_anti_aliasing()
            self.plotter.ren_win.LineSmoothingOff()
            self.plotter.ren_win.PolygonSmoothingOff()

    def load_fps(self):
        """Configure fps management."""
        if self.show_fps:
            self.fps = 0
            self.fps_actor = self.plotter.add_text(
                "fps: 0", self.fps_position, font_size=self.font_size)
            self.plotter.add_callback(self.compute_fps)

    def compute_fps(self):
        """Compute the frames per second."""
        fps = 1.0 / self.plotter.renderer.GetLastRenderTimeInSeconds()
        if self.show_fps:
            self.fps = np.round(fps).astype(np.int)
            self.fps_actor.SetInput("fps: {}".format(self.fps))
            self.fps_actor.SetPosition(self.fps_position)
        return fps
