"""Module about the application settings."""

import numpy as np
from qtpy.QtGui import QColor
from qtpy.QtCore import Signal
from qtpy.QtWidgets import (QPushButton, QDialog, QVBoxLayout, QHBoxLayout,
                            QListWidget, QStackedWidget, QWidget, QLabel,
                            QDoubleSpinBox, QSpinBox, QCheckBox,
                            QGroupBox, QComboBox, QLineEdit, QMessageBox,
                            QColorDialog)
from .utils import _rgb2str, _qrgb2rgb
from .params import rcParams, write_params


class SettingDialog(QDialog):
    """Manage the application settings."""

    def __init__(self, params, parent=None):
        """Initialize the SettingDialog."""
        super().__init__(parent)
        self.params = params
        self.copy_params = dict(self.params)

        vlayout = QVBoxLayout()

        # core widget
        core_layout = self._load_core_widget()
        vlayout.addLayout(core_layout)

        # buttons
        button_layout = self._load_buttons()
        vlayout.addLayout(button_layout)

        self.setWindowTitle("Setting")
        self.setModal(True)
        self.setLayout(vlayout)

    def _load_buttons(self):
        self.reset_dialog = QMessageBox(self)
        self.reset_dialog.setWindowTitle("Warning - Reset")
        self.reset_dialog.setText(
            "Are you sure that you want to reset the setting?"
        )
        self.reset_dialog.setInformativeText(
            "<b>Restart required to update the changes.</b>"
        )
        self.reset_dialog.setStandardButtons(
            QMessageBox.Cancel | QMessageBox.Ok
        )

        self.apply_dialog = QMessageBox(self)
        self.apply_dialog.setWindowTitle("Warning - Apply")
        self.apply_dialog.setText(
            "Are you sure that you want to apply this setting?"
        )
        self.apply_dialog.setInformativeText(
            "<b>Restart required to update the changes.</b>"
        )
        self.apply_dialog.setStandardButtons(
            QMessageBox.Cancel | QMessageBox.Ok
        )

        def _reset_params(button):
            if self.reset_dialog.standardButton(button) == QMessageBox.Ok:
                write_params(rcParams)
                self.copy_params = dict(rcParams)
            self.reset_dialog.close()
        self.reset_dialog.buttonClicked.connect(_reset_params)

        def _apply_params(button):
            if self.apply_dialog.standardButton(button) == QMessageBox.Ok:
                write_params(self.copy_params)
            self.apply_dialog.close()
        self.apply_dialog.buttonClicked.connect(_apply_params)

        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_dialog.show)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_dialog.show)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.ok_button)
        return button_layout

    def _load_core_widget(self):
        setting = self.params["setting"]
        hlayout = QHBoxLayout()
        list_widget = QListWidget()
        stacked_widget = QStackedWidget()
        for key in setting.keys():
            list_widget.addItem(key)
            widget = QWidget()
            widget_layout = QVBoxLayout()
            for value in setting[key]:
                self._create_form(widget_layout, [value])
            widget_layout.addStretch()
            widget.setLayout(widget_layout)
            stacked_widget.addWidget(widget)
        hlayout.addWidget(list_widget)
        hlayout.addWidget(stacked_widget)
        hlayout.setStretch(0, 1)
        hlayout.setStretch(1, 5)

        list_widget.currentRowChanged.connect(stacked_widget.setCurrentIndex)
        list_widget.setCurrentRow(0)
        return hlayout

    def _create_dropdown(self, layout, value, path):
        def _atomic_set_str(value):
            local_params = self.copy_params
            for path_element in path:
                local_params = local_params[path_element]
            local_params["value"] = value

        widget = QComboBox()
        for element in value["range"]:
            widget.addItem(element)
        widget.setCurrentText(value["value"])
        widget.currentTextChanged.connect(_atomic_set_str)
        layout.addWidget(widget)
        self.test_dropdown = widget  # for testing

    def _create_form_field_layout(self, layout, widget, name):
        if isinstance(name, str):
            widget_layout = QHBoxLayout()
            widget_layout.addWidget(QLabel(name))
            widget_layout.addWidget(widget)
            layout.addLayout(widget_layout)
            self.test_input_field = widget  # for testing
        else:
            layout.addWidget(widget)
            self.test_input_vector_field = widget  # for testing

    def _create_form_field(self, layout, value, path, name=None):
        def _atomic_set(value):
            local_params = self.copy_params
            for path_element in path[:-1]:
                local_params = local_params[path_element]
            if isinstance(name, str):
                local_params[path[-1]] = value
            else:
                local_params[path[-1]][name] = value

        if isinstance(value, bool):
            widget = QCheckBox()
            widget.setChecked(value)
            widget.toggled.connect(_atomic_set)
            self._create_form_field_layout(layout, widget, name)
        elif isinstance(value, str):
            widget = QLineEdit()
            widget.setText(value)
            widget.textChanged.connect(_atomic_set)
            self._create_form_field_layout(layout, widget, name)
        elif isinstance(value, int):
            widget = QSpinBox()
            # XXX: this could be improved surely
            widget.setMaximum(2000)
            widget.setValue(value)
            widget.valueChanged.connect(_atomic_set)
            self._create_form_field_layout(layout, widget, name)
        elif isinstance(value, float):
            widget = QDoubleSpinBox()
            widget.setValue(value)
            widget.valueChanged.connect(_atomic_set)
            self._create_form_field_layout(layout, widget, name)
        elif isinstance(value, list):
            if len(value) == 3 and "color" in path:
                widget = ColorButton()
                widget.setColor(value, is_int=False)
                widget.colorChanged.connect(_atomic_set)
                self._create_form_field_layout(layout, widget, name)
            else:
                widget_layout = QHBoxLayout()
                widget_layout.addWidget(QLabel(name))
                widget_layout.setStretch(0, len(value))
                for idx, element in enumerate(value):
                    self._create_form_field(widget_layout, element, path, idx)
                    widget_layout.setStretch(1 + idx, 1)
                layout.addLayout(widget_layout)

    def _create_form(self, layout, path):
        local_params = self.params
        for path_element in path:
            local_params = local_params[path_element]
        value = local_params

        if isinstance(value, dict):
            if "dropdown" in value:
                hlayout = QHBoxLayout()
                hlayout.addWidget(QLabel(path[-1]))
                self._create_dropdown(hlayout, value, path)
                layout.addLayout(hlayout)
            else:
                vlayout = QVBoxLayout()
                group = QGroupBox(path[-1])
                for key in value.keys():
                    self._create_form(vlayout, path + [key])
                group.setLayout(vlayout)
                layout.addWidget(group)
        else:
            self._create_form_field(layout, value, path, path[-1])


class ColorButton(QPushButton):
    """Select a color interactively."""

    colorChanged = Signal(list)

    def __init__(self, parent=None):
        """Initialize the ColorButton."""
        super().__init__(parent=parent)
        self.color_dialog = QColorDialog(self)
        self.clicked.connect(self.color_dialog.show)
        self.setObjectName("ColorButton")
        self.color_dialog.colorSelected.connect(self.setColor)

    def setColor(self, color, is_int=True):
        """Set the current button color."""
        if isinstance(color, QColor):
            color = _qrgb2rgb(color)
        color = np.asarray(color)
        self.setStyleSheet(
            "#ColorButton{background-color: rgb" +
            _rgb2str(color, is_int) + "}")
        if is_int:
            self.colorChanged.emit(list(color / 255.))
