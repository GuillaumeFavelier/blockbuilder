import os
import pytest
from blockbuilder.builder import Builder


@pytest.mark.xfail(os.environ.get("AZURE_CI_LINUX", False))
def test_builder(qtbot):
    builder = Builder(testing=True)
    qtbot.addWidget(builder)
    builder.close()
