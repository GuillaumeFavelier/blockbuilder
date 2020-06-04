import numpy as np
from blockbuilder.utils import _hasattr
from blockbuilder.selector import Selector


def test_selector():
    selector = Selector()
    assert all(np.equal(selector.dimensions, [2, 2, 2]))
    assert _hasattr(selector, "coords", type(None))
    assert _hasattr(selector, "coords_type", type)
    assert selector.selection() is None

    # requires an actor (i.e. plotter)
    # selector.hide()
    # selector.show()

    coords = np.asarray([0, 0, 0])
    selector.select(coords)
    assert all(np.equal(selector.selection(), coords))
