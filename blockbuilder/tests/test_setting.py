import os
from qtpy.QtWidgets import QMessageBox
from blockbuilder.params import rcParams
from blockbuilder.setting import SettingDialog, ColorButton


def test_setting_dialog(qtbot, tmpdir):
    # use a temporary configuration file to avoid
    # modifying the default one.
    output_dir = str(tmpdir.mkdir("tmpdir"))
    assert os.path.isdir(output_dir)
    filename = str(os.path.join(output_dir, "tmp.json"))
    os.environ["BB_TESTING"] = filename

    dialog = SettingDialog(rcParams)
    qtbot.addWidget(dialog)

    assert not dialog.isVisible()
    with qtbot.waitExposed(dialog):
        dialog.show()
    assert dialog.isVisible()
    dialog.test_input_field.setText("foo")
    dialog.test_input_vector_field.setValue(0)
    dialog.test_dropdown.setItemText(0, "foo")

    _dialog_scenario(qtbot, dialog.apply_button, dialog.apply_dialog)
    _dialog_scenario(qtbot, dialog.reset_button, dialog.reset_dialog)

    dialog.ok_button.click()
    assert not dialog.isVisible()
    dialog.close()


def _dialog_scenario(qtbot, button, dialog):
    for msg in [QMessageBox.Ok, QMessageBox.Cancel]:
        with qtbot.waitExposed(dialog):
            button.click()
        dialog.button(msg).click()


def test_color_button(qtbot):
    button = ColorButton()
    qtbot.addWidget(button)
    with qtbot.waitExposed(button.color_dialog, timeout=16000):
        button.click()
    button.color_dialog.accept()
    button.close()
