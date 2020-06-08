from blockbuilder.params import rcParams
from blockbuilder.setting import SettingDialog


def test_main_plotter_action_setting_dialog(qtbot):
    dialog = SettingDialog(rcParams)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.test_input_field.setValue(0)
    dialog.test_input_vector_field.setValue(0)
    dialog.test_dropdown.setItemText(0, "foo")
    dialog.apply_button.click()
    dialog.reset_button.click()
    dialog.cancel_button.click()
    dialog.close()
