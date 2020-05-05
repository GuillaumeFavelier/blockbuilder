"""Module about the default values."""

rcParams = {
    "unit": 1.,
    "origin": (0., 0., 0.),
    "graphics": {
        "pyvista_menu_bar": False,
        "pyvista_toolbar": False,
        "window_size": (1280, 720),
        "show_edges": True,
        "line_width": 2,
        "advanced": True,
        "show_fps": True,
        "fps_position": (2, 2),
        "font_size": 12,
        "background_top_color": (0.05, 0.05, 0.05),
        "background_bottom_color": (0., 0., .35),
    },
    "base": {
        "edge_color_offset": (.15, .15, .15),
    },
    "grid": {
        "color": {
            "build": (.05, .05, .35),
            "delete": (.35, .05, .05),
        },
        "opacity": .7,
    },
    "plane": {
        "color": (0.4, 0.4, 0.4),
        "opacity": 1.,
    },
    "selector": {
        "color": {
            "build": (.3, .3, .8),
            "delete": (.8, .3, .3),
        },
        "opacity": .7,
    },
    "block": {
        "color_array": "color",
        "color": (1., 1., 1., 1.),
        "edge_color": (.0, .0, .0),
    },
    "builder": {
        "dimensions": (32, 32, 32),
        "azimuth": 0,
        "azimuth_rng": (0, 360),
        "elevation": 45,
        "elevation_rng": (15, 165),
        "benchmark": {
            "enabled": False,
            "dimensions": (50, 50, 50),
            "number_of_runs": 10,
        },
    }
}
