"""Module about the default values."""

import os
from pathlib import Path
import json


rcParams = {
    "unit": 1.,
    "origin": [0., 0., 0.],
    "dimensions": [32, 32, 32],
    "plotter": {
        "window_size": [1280, 720],
        "show_edges": True,
        "line_width": 3,
        "advanced": True,
        "background": {
            "color": {
                "top": [0.05, 0.05, 0.05],
                "bottom": [0., 0., .35],
            },
        },
    },
    "element": {
        "edge_color_offset": [.15, .15, .15],
    },
    "grid": {
        "color": {
            "build": [.05, .05, .35],
            "delete": [.35, .05, .05],
        },
        "opacity": .7,
    },
    "plane": {
        "color": [0.4, 0.4, 0.4],
        "opacity": 1.,
    },
    "selector": {
        "color": {
            "build": [.3, .3, .8],
            "delete": [.8, .3, .3],
        },
        "opacity": .7,
    },
    "block": {
        "color_array_name": "color",
        "color": [.7, .7, .7],
        "edge": {
            "color": [.0, .0, .0],
        },
        "merge_policy": {
            "dropdown": True,
            "range": ["external", "internal"],
            "value": "external",
        },
    },
    "camera": {
        "view_up": [0, 0, 1],
        "azimuth": 0,
        "azimuth_rng": [0, 360],
        "elevation": 45,
        "elevation_rng": [15, 165],
    },
    "keybinding": {
        "distance_minus": {
            "dropdown": True,
            "range": ["Up"],
            "value": "Up",
        },
        "distance_plus": {
            "dropdown": True,
            "range": ["Down"],
            "value": "Down",
        },
        "azimuth_minus": {
            "dropdown": True,
            "range": ["q", "a"],
            "value": "q",
        },
        "azimuth_plus": {
            "dropdown": True,
            "range": ["d"],
            "value": "d",
        },
        "elevation_minus": {
            "dropdown": True,
            "range": ["z", "w"],
            "value": "z",
        },
        "elevation_plus": {
            "dropdown": True,
            "range": ["s"],
            "value": "s",
        },
    },
    "builder": {
        "toggles": {
            "area": False,
            "edges": True,
        },
        "toolbar": {
            "area": {
                "dropdown": True,
                "range": ["left", "right", "top", "bottom"],
                "value": "top",
            },
            "icon_size": [36, 36],
        },
    },
    "app": {
        "name": "BlockBuilder",
        "icon": "blockbuilder.svg",
    },
    "setting": {
        "interface": ["plotter", "builder"],
        "scene": ["dimensions", "grid", "plane", "selector", "block"],
        "keys": ["keybinding"],
        "dev": ["unit", "origin", "element", "camera", "app"],
    },
}


def get_config_path():
    """Get the default config path."""
    home_path = Path.home()
    env_variable = "BB_TESTING"
    config_file = "blockbuilder.json"
    config_name = os.environ.get(env_variable, config_file)
    return home_path.joinpath(config_name)


def set_params(params):
    """Create the default configuration settings."""
    config_path = get_config_path()
    with open(config_path, 'w') as fp:
        json.dump(params, fp)


def signature(params):
    """Create a params str signature."""
    def _signature(params, sig):
        for key in params.keys():
            sig.append(key)
            if isinstance(params[key], dict):
                _signature(params[key], sig)

    my_list = list()
    _signature(params, my_list)
    return '/'.join(my_list)


def get_params():
    """Create or load the default configuration settings."""
    params = rcParams
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, 'r') as fp:
            params = json.loads(fp.read())
        if signature(params) != signature(rcParams):
            set_params(rcParams)
            return rcParams
    else:
        set_params(params)
    return params
