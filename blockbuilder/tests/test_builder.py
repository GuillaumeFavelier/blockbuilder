import os
import pytest
from blockbuilder.builder import Builder


@pytest.mark.skipif(os.environ.get("AZURE_CI_LINUX", False),
                    reason="Bug with pyvirtualdisplay")
def test_builder(qtbot):
    builder = Builder(testing=True)
    qtbot.addWidget(builder)
    builder.close()
