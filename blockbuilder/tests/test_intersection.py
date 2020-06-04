import numpy as np
import pytest
import vtk
from blockbuilder.element import ElementId
from blockbuilder.intersection import Intersection


class FakeActor(vtk.vtkActor):
    def __init__(self, element_id):
        super().__init__()
        self.element_id = element_id


class FakePicker(vtk.vtkPicker):
    def __init__(self, element_id, position, no_pick=True):
        super().__init__()
        self.no_pick = no_pick
        self.cell_id = 0
        self.points = vtk.vtkPoints()
        self.points.SetNumberOfPoints(1)
        self.points.SetPoint(0, position)
        actor = FakeActor(element_id)
        self.actors = vtk.vtkActorCollection()
        self.actors.AddItem(actor)

    def GetCellId(self):
        if self.no_pick:
            return -1
        else:
            return self.cell_id

    def GetPickedPositions(self):
        return self.points

    def GetActors(self):
        return self.actors


@pytest.mark.parametrize('no_pick', [
    True,
    False,
    ])
def test_intersection(no_pick):
    for element_id in ElementId:
        position = np.random.rand(3)
        picker = FakePicker(element_id, position, no_pick)
        intersection = Intersection(picker)
        assert no_pick == (not intersection.exist())
        if not no_pick:
            assert intersection.element(element_id)
            assert np.allclose(position, intersection.point(element_id))
