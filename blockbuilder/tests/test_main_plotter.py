from blockbuilder.main_plotter import MainPlotter


def test_main_plotter(qtbot):
    plotter = MainPlotter(testing=True)
    qtbot.addWidget(plotter)
    plotter.close()
