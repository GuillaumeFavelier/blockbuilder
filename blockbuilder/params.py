"""Module about the default values."""

rcParams = {
    "unit": 1.,
    "origin": (0., 0., 0.),
    "plotter": {
        "window_size": (1280, 720),
        "show_edges": True,
        "line_width": 3,
        "advanced": True,
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
        "color_array_name": "color",
        "color": (.7, .7, .7),
        "edge_color": (.0, .0, .0),
        "merge_policies": ["external", "internal"],
        "merge_policy": "external",
    },
    "builder": {
        "name": "BlockBuilder",
        "dimensions": (32, 32, 32),
        "azimuth": 0,
        "azimuth_rng": (0, 360),
        "elevation": 45,
        "elevation_rng": (15, 165),
        "bindings": {
            "distance_minus": "Up",
            "distance_plus": "Down",
            "azimuth_minus": "q",
            "azimuth_plus": "d",
            "elevation_minus": "z",
            "elevation_plus": "s",
        },
        "toggles": {
            "select": False,
            "edges": True,
        },
    }
}
