import os
from blockbuilder.params import rcParams
from blockbuilder.setting import SettingDialog

event_delay = 300


def test_main_plotter_action_setting_dialog(qtbot, tmpdir):
    # use a temporory configuration file to avoid
    # modifying the default one.
    output_dir = str(tmpdir.mkdir("tmpdir"))
    assert os.path.isdir(output_dir)
    filename = str(os.path.join(output_dir, "tmp.json"))
    os.environ["BB_TESTING"] = filename

    dialog = SettingDialog(rcParams)
    qtbot.addWidget(dialog)
    with qtbot.wait_exposed(dialog, event_delay):
        dialog.show()
    dialog.test_input_field.setText("foo")
    dialog.test_input_vector_field.setValue(0)
    dialog.test_dropdown.setItemText(0, "foo")
    dialog.apply_button.click()
    dialog.reset_button.click()
    dialog.cancel_button.click()
    dialog.close()
