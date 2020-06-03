from blockbuilder.params import rcParams


def test_params():
    assert isinstance(rcParams, dict)
    # Empty dictionaries evaluate to False in Python
    assert rcParams
