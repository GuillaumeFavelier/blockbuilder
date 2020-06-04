from blockbuilder.element import ElementId
from blockbuilder.grid import Grid


def test_grid():
    dimensions = [3, 3, 3]
    grid = Grid(dimensions=dimensions)

    assert grid.element_id == ElementId.GRID
    assert grid.dimensions[2] == 1
