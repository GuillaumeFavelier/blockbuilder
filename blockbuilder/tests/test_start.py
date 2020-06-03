from blockbuilder.app import start


def test_start(qtbot):
    builder = start.main(True)
    qtbot.addWidget(builder)
