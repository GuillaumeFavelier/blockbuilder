from blockbuilder.builder import Builder


def test_builder(qtbot):
    builder = Builder(testing=True)
    qtbot.addWidget(builder)
    builder.close()
