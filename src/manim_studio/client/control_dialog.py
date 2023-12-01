from PyQt6.QtWidgets import QVBoxLayout, QLabel, QSlider, QColorDialog, QComboBox, QLineEdit, QTextEdit, QCheckBox, \
    QPushButton, QScrollArea, QGroupBox, QDoubleSpinBox, QHBoxLayout, QFileDialog
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import socket
import numpy as np
import os
import sys


class ClientControls(QScrollArea):
    """A widget to display the controls of the scene in Manim Studio Client."""

    add_slider_to_client = pyqtSignal(str, str, str, str, str)
    add_color_widget_to_client = pyqtSignal(str, int, int, int, int)
    add_dropdown_to_client = pyqtSignal(str, list, str)
    add_line_edit_to_client = pyqtSignal(str, str)
    add_text_editor_to_client = pyqtSignal(str, str)
    add_checkbox_to_client = pyqtSignal(str, bool)
    add_button_to_client = pyqtSignal(str)
    add_position_control_to_client = pyqtSignal(str, np.ndarray)
    set_control_value = pyqtSignal(str, str)
    add_file_widget_to_client = pyqtSignal(str, str)
    add_spin_box_to_client = pyqtSignal(str, float)
    close_signal = pyqtSignal()

    def __init__(self, main, s: socket.socket, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main = main
        self.setWindowTitle("Manim Studio Client - Controls")
        self.layout_ = QVBoxLayout()
        self.controls = {}
        self.setLayout(self.layout_)
        self.label = QLabel(text="No controls defined")
        self.layout().addWidget(self.label)
        self.s = s
        self.add_slider_to_client.connect(
            self.add_slider_to_client_command)
        self.add_color_widget_to_client.connect(
            self.add_color_widget_to_client_command)
        self.add_dropdown_to_client.connect(
            self.add_dropdown_to_client_command)
        self.add_line_edit_to_client.connect(
            self.add_line_edit_to_client_command)
        self.add_text_editor_to_client.connect(
            self.add_text_editor_to_client_command)
        self.add_checkbox_to_client.connect(
            self.add_checkbox_to_client_command)
        self.add_button_to_client.connect(
            self.add_button_to_client_command)
        self.set_control_value.connect(
            self.set_control_value_command)
        self.add_position_control_to_client.connect(
            self.add_position_control_to_client_command)
        self.add_file_widget_to_client.connect(
            self.add_file_widget_to_client_command)
        self.add_spin_box_to_client.connect(
            self.add_spin_box_to_client_command)
        self.close_signal.connect(self.close)
        self.update_controls_thread = UpdateControlsThread(
            self.s,
            add_slider_to_client=self.add_slider_to_client,
            add_color_widget_to_client=self.add_color_widget_to_client,
            add_dropdown_to_client=self.add_dropdown_to_client,
            add_line_edit_to_client=self.add_line_edit_to_client,
            add_text_editor_to_client=self.add_text_editor_to_client,
            add_checkbox_to_client=self.add_checkbox_to_client,
            add_button_to_client=self.add_button_to_client,
            add_position_control_to_client=self.add_position_control_to_client,
            add_file_widget_to_client=self.add_file_widget_to_client,
            add_spin_box_to_client=self.add_spin_box_to_client,
            close_signal=self.close_signal,
            set_control_value=self.set_control_value)
        self.update_controls_thread.start()

    def set_control_value_command(self, name, value):
        if name in self.controls:
            control = self.controls[name]
            if isinstance(control, QSlider):
                control.setValue(int(value))
            elif isinstance(control, QColorDialog):
                r, g, b, a = value.split(",")
                control.setCurrentColor(
                    QColor(int(r), int(g), int(b), int(a)))
            elif isinstance(control, QComboBox):
                control.setCurrentText(value)
            elif isinstance(control, QLineEdit):
                control.setText(value)
            elif isinstance(control, QTextEdit):
                control.setText(value)
            elif isinstance(control, QCheckBox):
                control.setChecked(value == "True")
            elif isinstance(control, QGroupBox):
                x, y, z = value.split(",")
                control.x_.setValue(float(x))
                control.y_.setValue(float(y))
                control.z_.setValue(float(z))
            else:
                return
        else:
            return

    def add_spin_box_to_client_command(self, name, default):
        if self.label.isVisible():
            self.label.hide()
        name_label = QLabel(text=name)
        spin_box = QDoubleSpinBox()
        spin_box.setRange(-sys.float_info.max, sys.float_info.max)
        spin_box.setValue(default)
        spin_box.valueChanged.connect(
            lambda value: self.s.sendall(f"set_spin_box_value {name} {value}".encode("utf-8")))
        self.layout().addWidget(name_label)
        self.layout().addWidget(spin_box)
        self.controls[name] = spin_box

    def add_file_widget_to_client_command(self, name, file_flags):
        if self.label.isVisible():
            self.label.hide()
        widget = QGroupBox(name)
        widget.setTitle(name)
        widget.setLayout(QVBoxLayout())
        widget.name_label = QLabel(name)
        widget.file_path_label = QLabel()
        widget.file_size_label = QLabel()
        widget.file_flags = file_flags
        widget.select_file_button = QPushButton("Select File")
        widget.select_file_button.clicked.connect(
            self.select_file_command)
        widget.clear_file_button = QPushButton("Clear File")
        widget.clear_file_button.clicked.connect(
            self.clear_file_command)
        widget.clear_file_button.setEnabled(False)
        widget.layout().addWidget(widget.name_label)
        widget.layout().addWidget(widget.file_path_label)
        widget.layout().addWidget(widget.file_size_label)
        widget.layout().addWidget(widget.select_file_button)
        widget.layout().addWidget(widget.clear_file_button)
        self.layout().addWidget(widget)
        self.controls[name] = widget

    def select_file_command(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", self.controls[self.sender().parent().title()].file_flags)
        if file_name:
            self.controls[self.sender().parent().title()].file_path_label.setText(
                file_name)
            self.controls[self.sender().parent().title()].file_size_label.setText(
                f"File Size: {os.path.getsize(file_name)} bytes")
            self.controls[self.sender().parent().title()].clear_file_button.setEnabled(
                True)
            with open(file_name, "rb") as f:
                self.s.sendall(f"set_file_widget_value?{self.sender().parent().title()}?".encode("utf-8")
                               + f"{file_name}?".encode("utf-8") +
                               f"{os.path.getsize(file_name)}?".encode("utf-8") + f.read())

    def clear_file_command(self):
        self.controls[self.sender().parent().title()].file_path_label.setText(
            "")
        self.controls[self.sender().parent().title()].file_size_label.setText(
            "")
        self.controls[self.sender().parent().title()].clear_file_button.setEnabled(
            False)
        self.s.sendall(f"set_file_widget_value?{self.sender().parent().title()}".encode("utf-8") +
                       "?<None?<None?<None".encode("utf-8"))

    def add_slider_to_client_command(self, name, min_, max_, step, default):
        if self.label.isVisible():
            self.label.hide()
        name_label = QLabel(text=name)
        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_))
        slider.setMaximum(int(max_))
        slider.setSingleStep(int(step))
        slider.setValue(int(default))
        slider.valueChanged.connect(
            lambda value: self.s.sendall(f"set_slider_value {name} {value}".encode("utf-8")))
        self.layout().addWidget(name_label)
        self.layout().addWidget(slider)
        self.controls[name] = slider

    def add_color_widget_to_client_command(self, name, r, g, b, a):
        if self.label.isVisible():
            self.label.hide()
        name_label = QLabel(text=name)
        color_dialog = QColorDialog()
        color_dialog.setCurrentColor(
            QColor(int(r), int(g), int(b), int(a)))
        color_dialog.currentColorChanged.connect(
            lambda color: self.s.sendall(f"set_color {name} {color.red()} {color.green()} {color.blue()} {color.alpha()}".encode("utf-8")))
        self.layout().addWidget(name_label)
        self.layout().addWidget(color_dialog)
        self.controls[name] = color_dialog

    def add_dropdown_to_client_command(self, name, options, default):
        if self.label.isVisible():
            self.label.hide()
        name_label = QLabel(text=name)
        dropdown = QComboBox()
        dropdown.addItems(options)
        dropdown.setCurrentText(default)
        dropdown.currentTextChanged.connect(
            lambda text: self.s.sendall(f"set_dropdown {name} {text}".encode("utf-8")))
        self.layout().addWidget(name_label)
        self.layout().addWidget(dropdown)
        self.controls[name] = dropdown

    def add_line_edit_to_client_command(self, name, default):
        if self.label.isVisible():
            self.label.hide()
        name_label = QLabel(text=name)
        line_edit = QLineEdit()
        line_edit.setText(default)
        line_edit.textChanged.connect(
            lambda text: self.s.sendall(f"set_line_edit {name} {text}".encode("utf-8")))
        self.layout().addWidget(name_label)
        self.layout().addWidget(line_edit)
        self.controls[name] = line_edit

    def add_text_editor_to_client_command(self, name, default):
        if self.label.isVisible():
            self.label.hide()
        name_label = QLabel(text=name)
        text_edit = QTextEdit()
        text_edit.setText(default)
        text_edit.textChanged.connect(
            lambda text: self.s.sendall(f"set_text_edit {name} {text}".encode("utf-8")))
        self.layout().addWidget(name_label)
        self.layout().addWidget(text_edit)
        self.controls[name] = text_edit

    def add_checkbox_to_client_command(self, name, default):
        if self.label.isVisible():
            self.label.hide()
        name_label = QLabel(text=name)
        checkbox = QCheckBox()
        checkbox.setChecked(default == "True")
        checkbox.stateChanged.connect(
            lambda: self.s.sendall(f"set_checkbox {name} {checkbox.isChecked()}".encode("utf-8")))
        self.layout().addWidget(name_label)
        self.layout().addWidget(checkbox)
        self.controls[name] = checkbox

    def add_button_to_client_command(self, name):
        if self.label.isVisible():
            self.label.hide()
        name_label = QLabel(text=name)
        button = QPushButton(text=name)
        button.clicked.connect(
            lambda: self.s.sendall(f"button_clicked {name}".encode("utf-8")))
        self.layout().addWidget(name_label)
        self.layout().addWidget(button)
        self.controls[name] = button

    def close(self):
        super().close()
        self.main.close()
        self.s.close()

    def add_position_control_to_client_command(self, name, default):
        if self.label.isVisible():
            self.label.hide()
        widget = QGroupBox(name)
        widget.setLayout(QHBoxLayout())
        widget.x_ = QDoubleSpinBox()
        widget.x_.setValue(default[0])
        widget.y_ = QDoubleSpinBox()
        widget.y_.setValue(default[1])
        widget.z_ = QDoubleSpinBox()
        widget.z_.setValue(default[2])
        widget.x_.valueChanged.connect(
            lambda value: self.s.sendall(f"set_position_control_value_x {name} {value}".encode("utf-8")))
        widget.y_.valueChanged.connect(
            lambda value: self.s.sendall(f"set_position_control_value_y {name} {value}".encode("utf-8")))
        widget.z_.valueChanged.connect(
            lambda value: self.s.sendall(f"set_position_control_value_z {name} {value}".encode("utf-8")))
        widget.display_dot_checkbox = QCheckBox("Display Dot")
        widget.display_dot_checkbox.setChecked(False)
        widget.display_dot_checkbox.stateChanged.connect(
            lambda: self.s.sendall(f"set_position_control_display_dot {name} {widget.display_dot_checkbox.isChecked()}".encode("utf-8")))
        widget.layout().addWidget(widget.x_)
        widget.layout().addWidget(widget.y_)
        widget.layout().addWidget(widget.z_)
        widget.layout().addWidget(widget.display_dot_checkbox)
        self.layout().addWidget(widget)
        self.controls[name] = widget


class UpdateControlsThread(QThread):
    def __init__(self,
                 s: socket.socket,
                 add_slider_to_client: pyqtSignal,
                 add_color_widget_to_client: pyqtSignal,
                 add_dropdown_to_client: pyqtSignal,
                 add_line_edit_to_client: pyqtSignal,
                 add_text_editor_to_client: pyqtSignal,
                 add_checkbox_to_client: pyqtSignal,
                 add_button_to_client: pyqtSignal,
                 add_position_control_to_client: pyqtSignal,
                 add_file_widget_to_client: pyqtSignal,
                 add_spin_box_to_client: pyqtSignal,
                 close_signal: pyqtSignal,
                 set_control_value: pyqtSignal):
        super().__init__()
        self.s = s
        self.add_slider_to_client = add_slider_to_client
        self.add_color_widget_to_client = add_color_widget_to_client
        self.add_dropdown_to_client = add_dropdown_to_client
        self.add_line_edit_to_client = add_line_edit_to_client
        self.add_text_editor_to_client = add_text_editor_to_client
        self.add_checkbox_to_client = add_checkbox_to_client
        self.add_button_to_client = add_button_to_client
        self.add_position_control_to_client = add_position_control_to_client
        self.add_file_widget_to_client = add_file_widget_to_client
        self.add_spin_box_to_client = add_spin_box_to_client
        self.close_signal = close_signal
        self.set_control_value = set_control_value

    def run(self):
        self.s.sendall(b"get_controls")
        while True:
            try:
                msg = self.s.recv(1024)
            except ConnectionResetError:
                break
            command = msg.decode("utf-8")
            if command == "no_controls":
                continue
            if command.startswith("add_slider"):
                _, name, default, min_, max_, step = command.split(" ")
                self.add_slider_to_client.emit(
                    name, min_, max_, step, default)
            elif command.startswith("add_color_widget"):
                _, name, r, g, b, a = command.split(" ")
                self.add_color_widget_to_client.emit(
                    name, r, g, b, a)
            elif command.startswith("add_dropdown"):
                _, name, options, default = command.split(" ")
                options = options.split(",")
                self.add_dropdown_to_client.emit(
                    name, options, default)
            elif command.startswith("add_line_editor_widget"):
                _, name, *words = command.split(" ")
                self.add_line_edit_to_client.emit(
                    name, " ".join(words))
            elif command.startswith("add_text_editor_widget"):
                _, name, *words = command.split(" ")
                self.add_text_editor_to_client.emit(
                    name, " ".join(words))
            elif command.startswith("add_checkbox"):
                _, name, default = command.split(" ")
                self.add_checkbox_to_client.emit(
                    name, default == "True")
            elif command.startswith("add_button"):
                _, name = command.split(" ")
                self.add_button_to_client.emit(name)
            elif command.startswith("add_position_control"):
                _, name, *default = command.split(" ")
                x, y, z = default
                x = float(x)
                y = float(y)
                z = float(z)
                self.add_position_control_to_client.emit(
                    name, np.array([x, y, z]))
            elif command.startswith("add_file_widget"):
                _, name, *file_flags = command.split(" ")
                file_flags = " ".join(file_flags)
                self.add_file_widget_to_client.emit(name, file_flags)
            elif command.startswith("add_spin_box"):
                _, name, default = command.split(" ")
                self.add_spin_box_to_client.emit(name, float(default))
            elif command == "exit":
                self.close_signal.emit()
                break
            else:
                continue
