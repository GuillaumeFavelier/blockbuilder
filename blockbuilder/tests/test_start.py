import os
from blockbuilder.app import start


def test_start(qtbot, tmpdir):
    output_dir = str(tmpdir.mkdir("tmpdir"))
    assert os.path.isdir(output_dir)
    filename = str(os.path.join(output_dir, "config.json"))
    os.environ["BB_TESTING"] = filename

    # create config
    plotter = start.main(True)
    qtbot.addWidget(plotter)
    plotter.close()

    # load config
    plotter = start.main(True)
    qtbot.addWidget(plotter)
    plotter.close()
