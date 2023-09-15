
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QWidget


class ControlDialog(QDialog):
    def __init__(self, controls: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Add controls to snippet")
        self.layout_ = QVBoxLayout()
        self.controls = controls
        self.addControlsCheckbox = QCheckBox("Add controls")
        self.addControlsCheckbox.setChecked(False)
        self.add_controls = False
        self.controls_toggle = {k: False for k in self.controls.keys()}
        self.addControlsCheckbox.stateChanged.connect(
            lambda: self.toggle_add_controls(self.addControlsCheckbox.isChecked()))
        self.controls_toggle_widget = QWidget()
        self.controls_toggle_layout = QVBoxLayout()
        self.controls_toggle_widget.setLayout(self.controls_toggle_layout)
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.layout_.addWidget(self.addControlsCheckbox)
        self.layout_.addWidget(self.okButton)
        self.layout_.addWidget(self.controls_toggle_widget)
        self.setLayout(self.layout_)

    def toggle_add_controls(self, state: bool):
        self.add_controls = state
        if state is True:
            self.controls_toggle = {k: False for k in self.controls.keys()}
            for name in self.controls.keys():
                checkbox = QCheckBox(name)
                checkbox.setChecked(False)
                checkbox.stateChanged.connect(
                    lambda: self.toggle_control(name, checkbox.isChecked()))
                self.controls_toggle_layout.addWidget(checkbox)
        else:
            for _ in range(len(self.controls.keys())):
                self.controls_toggle_layout.itemAt(0).widget().deleteLater()

    def toggle_control(self, name: str, state: bool):
        self.controls_toggle[name] = state
