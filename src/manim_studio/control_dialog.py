from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QWidget
from PyQt6.QtCore import Qt


class ControlDialog(QDialog):
    def __init__(self, controls: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Add controls to snippet")
        self.layout_ = QVBoxLayout()
        self.addControlsCheckbox = QCheckBox("Add controls")
        self.addControlsCheckbox.setChecked(False)
        self.add_controls = False
        self.controls_toggle = {k: False for k in controls.keys()}
        self.addControlsCheckbox.stateChanged.connect(self.toggle_add_controls)
        self.controls_toggle_widget = QWidget()
        self.controls_toggle_layout = QVBoxLayout()
        self.controls_toggle_widget.setLayout(self.controls_toggle_layout)
        for name in controls.keys():
            checkbox = QCheckBox(name)
            checkbox.setChecked(False)
            checkbox.stateChanged.connect(
                lambda state, name=name: self.toggle_control(name, state))
            self.controls_toggle_layout.addWidget(checkbox)
        self.controls_toggle_widget.hide()
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.layout_.addWidget(self.addControlsCheckbox)
        self.layout_.addWidget(self.okButton)
        self.layout_.addWidget(self.controls_toggle_widget)
        self.setLayout(self.layout_)

    def toggle_add_controls(self, state: bool):
        self.add_controls = bool(state)
        if self.add_controls:
            self.controls_toggle_widget.show()
        else:
            self.controls_toggle_widget.hide()

    def exec_and_return(self):
        self.exec()
        return self.add_controls, self.controls_toggle

    def toggle_control(self, name: str, state: bool):
        self.controls_toggle[name] = bool(state)
