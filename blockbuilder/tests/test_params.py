import os

from blockbuilder.params import get_params, signature


def test_params(tmpdir):
    # use a temporary configuration file to avoid
    # modifying the default one.
    output_dir = str(tmpdir.mkdir("tmpdir"))
    assert os.path.isdir(output_dir)
    filename = str(os.path.join(output_dir, "tmp.json"))
    os.environ["BB_TESTING"] = filename

    # create default config file
    assert not os.path.exists(filename)
    params = get_params()
    assert isinstance(params, dict)
    # Empty dictionaries evaluate to False in Python
    assert params
    assert os.path.isfile(filename)

    # reset the params in case of conflicts
    test_params = {"foo": -1}
    params = get_params(test_params)
    assert signature(params) == signature(test_params)

    # load the params
    params = get_params(test_params)
    assert signature(params) == signature(test_params)
