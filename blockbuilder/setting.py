"""Module about the application settings."""

from PyQt5.QtWidgets import (QPushButton, QDialog, QVBoxLayout, QHBoxLayout,
                             QListWidget, QStackedWidget, QWidget, QLabel,
                             QDoubleSpinBox, QSpinBox, QCheckBox,
                             QGroupBox, QComboBox, QLineEdit)


class SettingDialog(QDialog):
    """Manage the application settings."""

    def __init__(self, params, parent=None):
        """Initialize the SettingDialog."""
        super().__init__(parent)
        self.params = params
        copy_params = dict(self.params)

        def _create_dropdown(layout, value, path):
            def _atomic_set(value):
                local_params = copy_params
                for path_element in path:
                    local_params = local_params[path_element]
                local_params["value"] = value

            widget = QComboBox()
            for element in value["range"]:
                widget.addItem(element)
            widget.setCurrentText(value["value"])
            widget.currentTextChanged.connect(_atomic_set)
            layout.addWidget(widget)
            self.test_dropdown = widget  # for testing

        def _create_form_field_layout(layout, widget, name):
            if isinstance(name, str):
                widget_layout = QHBoxLayout()
                widget_layout.addWidget(QLabel(name))
                widget_layout.addWidget(widget)
                layout.addLayout(widget_layout)
                self.test_input_field = widget  # for testing
            else:
                layout.addWidget(widget)
                self.test_input_vector_field = widget  # for testing

        def _create_form_field(layout, value, path, name=None):
            def _atomic_set(value):
                local_params = copy_params
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
                _create_form_field_layout(layout, widget, name)
            elif isinstance(value, str):
                widget = QLineEdit()
                widget.setText(value)
                widget.textChanged.connect(_atomic_set)
                _create_form_field_layout(layout, widget, name)
            elif isinstance(value, int):
                widget = QSpinBox()
                widget.setMaximum(2000)
                widget.setValue(value)
                widget.valueChanged.connect(_atomic_set)
                _create_form_field_layout(layout, widget, name)
            elif isinstance(value, float):
                widget = QDoubleSpinBox()
                widget.setValue(value)
                widget.valueChanged.connect(_atomic_set)
                _create_form_field_layout(layout, widget, name)
            elif isinstance(value, list):
                widget_layout = QHBoxLayout()
                widget_layout.addWidget(QLabel(name))
                widget_layout.setStretch(0, len(value))
                for idx, element in enumerate(value):
                    _create_form_field(widget_layout, element, path, idx)
                    widget_layout.setStretch(1 + idx, 1)
                layout.addLayout(widget_layout)

        def _create_form(layout, path):
            local_params = self.params
            for path_element in path:
                local_params = local_params[path_element]
            value = local_params

            if isinstance(value, dict):
                if "dropdown" in value:
                    hlayout = QHBoxLayout()
                    hlayout.addWidget(QLabel(path[-1]))
                    _create_dropdown(hlayout, value, path)
                    layout.addLayout(hlayout)
                else:
                    vlayout = QVBoxLayout()
                    group = QGroupBox(path[-1])
                    for key in value.keys():
                        _create_form(vlayout, path + [key])
                    group.setLayout(vlayout)
                    layout.addWidget(group)
            else:
                _create_form_field(layout, value, path, path[-1])

        vlayout = QVBoxLayout()
        widget_connections = dict()

        # list widgets
        hlayout = QHBoxLayout()
        list_widget = QListWidget()
        stacked_widget = QStackedWidget()
        setting = self.params["setting"]
        for idx, key in enumerate(setting.keys()):
            list_widget.addItem(key)
            widget = QWidget()
            widget_layout = QVBoxLayout()
            for value in setting[key]:
                _create_form(widget_layout, [value])
            widget_layout.addStretch()
            widget.setLayout(widget_layout)
            stacked_widget.addWidget(widget)
            widget_connections[key] = idx
        hlayout.addWidget(list_widget)
        hlayout.addWidget(stacked_widget)
        hlayout.setStretch(0, 1)
        hlayout.setStretch(1, 5)
        vlayout.addLayout(hlayout)

        def _connect_item(item):
            idx = widget_connections[item.text()]
            stacked_widget.setCurrentIndex(idx)

        list_widget.currentItemChanged.connect(_connect_item)
        list_widget.setCurrentRow(0)

        def _reset_params():
            from .params import rcParams, set_params
            set_params(rcParams)

        def _apply_params():
            from .params import set_params
            set_params(copy_params)

        # buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply", self)
        self.apply_button.clicked.connect(_apply_params)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(_reset_params)
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        vlayout.addLayout(button_layout)

        self.setLayout(vlayout)
