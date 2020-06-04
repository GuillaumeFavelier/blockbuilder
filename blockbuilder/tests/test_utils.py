from blockbuilder.utils import _hasattr


def test_hasattr():
    class A():
        def __init__(self):
            self.a = True

    variable = A()
    assert _hasattr(variable, "a", bool)
    assert not _hasattr(variable, "b", bool)
