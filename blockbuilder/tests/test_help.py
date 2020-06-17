from blockbuilder.help import HelpDialog

from qtpy.QtGui import QIcon


def test_help_dialog(qtbot):
    icons = {"foo": QIcon(), "bar": QIcon()}
    short_desc = ["foo", "bar"]
    long_desc = ["FOO", "BAR"]
    icon_size = (32, 32)
    dialog = HelpDialog(icons, icon_size, short_desc, long_desc, None)
    qtbot.addWidget(dialog)

    assert not dialog.isVisible()
    dialog.show()
    qtbot.waitForWindowShown(dialog)
    assert dialog.isVisible()

    dialog.ok_button.click()
    assert not dialog.isVisible()
    dialog.close()
