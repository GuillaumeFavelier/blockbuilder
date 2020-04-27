rcParams = {
    "unit": 1.,
    "origin": (0., 0., 0.),
    "graphics": {
        "pyvista_menu_bar": False,
        "pyvista_toolbar": False,
        "window_size": (1280, 720),
        "line_width": 2,
        "advanced": True,
        "show_fps": True,
        "fps_position": (2, 2),
        "font_size": 12,
        "background_top_color": (0.05, 0.05, 0.05),
        "background_bottom_color": (0., 0., .35),
    },
    "grid": {
        "color_array": "color",
        "build_color": (.1, .1, .4),
        "delete_color": (.4, .1, .1),
        "show_edges": True,
        "opacity": .7,
    },
    "plane": {
        "color": (0.4, 0.4, 0.4),
        "show_edges": False,
        "opacity": 1.,
    },
    "selector": {
        "dimensions": (2, 2, 2),
        "build_color": (.3, .3, .8),
        "delete_color": (.8, .3, .3),
    },
    "block": {
        "color_array": "color",
        "color": (1., 1., 1.),
        "edge_color": (.0, .0, .0),
        "show_edges": True,
    },
    "builder": {
        "dimensions": (15, 15, 15),
        "benchmark": {
            "enabled": False,
            "dimensions": (50, 50, 50),
            "number_of_runs": 10,
        },
    }
}
