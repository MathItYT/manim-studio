from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QFileDialog, \
    QMenuBar, QMessageBox, QDialog, QLineEdit, QLabel, QCheckBox, QGridLayout, QScrollArea, \
    QDoubleSpinBox, QStatusBar, QComboBox
from PyQt6.QtGui import QAction, QIntValidator, QColor
from PyQt6.QtCore import pyqtSlot, Qt
import numpy as np
from pathlib import Path
import dill as pickle
import socket

from .communicate import Communicate
from .live_scene import LiveScene
from manim_studio.widgets.slider import Slider
from manim_studio.widgets.color_widget import ColorWidget
from manim_studio.widgets.dropdown_widget import DropdownWidget
from manim_studio.widgets.line_editor_widget import LineEditorWidget
from manim_studio.widgets.text_editor_widget import TextEditorWidget
from manim_studio.widgets.checkbox_widget import CheckboxWidget
from .control_dialog import ControlDialog
from manim_studio.widgets.button import Button
from manim_studio.widgets.position_control import PositionControl
from .code_edit import CodeEdit


class EditorWidget(QWidget):
    def __init__(self, communicate: Communicate, scene: LiveScene, server: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.communicate = communicate
        self.manim_studio_server = None
        self.server = server
        self.setWindowTitle("Manim Studio - Editor")
        self.scene = scene
        self.controls = dict()
        self.ready_to_save = True
        self.enter_your_code_label = QLabel(text="Enter your code below:")
        self.code_cell_edit = CodeEdit()

        self.send_button = QPushButton(
            "Send code (Ctrl+Return)")
        self.send_button.setGeometry(0, 0, 100, 50)
        self.send_button.setShortcut("Ctrl+Return")
        self.send_button.clicked.connect(self.send_code)
        self.end_button = QPushButton("End scene without saving (Ctrl+Q)")
        self.end_button.setGeometry(0, 0, 100, 50)
        self.end_button.setShortcut("Ctrl+Q")
        self.end_button.clicked.connect(self.end_scene)
        self.save_snip_button = QPushButton("Save snippet (Ctrl+Shift+S)")
        self.save_snip_button.setShortcut("Ctrl+Shift+S")
        self.save_snip_button.setGeometry(0, 0, 100, 50)
        self.save_snip_button.clicked.connect(self.save_snippet)
        self.save_snip_and_run_button = QPushButton(
            "Save snippet and run (Ctrl+Shift+Return)")
        self.save_snip_and_run_button.setShortcut("Ctrl+Shift+Return")
        self.save_snip_and_run_button.setGeometry(0, 0, 100, 50)
        self.save_snip_and_run_button.clicked.connect(
            self.save_snippet_and_run)
        self.communicate.save_snippet.connect(self.save_snippet_command)
        self.next_slide_button = QPushButton("Next slide (Ctrl+N)")
        self.next_slide_button.setShortcut("Ctrl+N")
        self.next_slide_button.setGeometry(0, 0, 100, 50)
        self.communicate.next_slide.connect(self.next_slide)
        self.next_slide_button.clicked.connect(
            self.communicate.next_slide.emit)
        self.pause_scene_button = QPushButton("Pause scene (Ctrl+P)")
        self.pause_scene_button.setShortcut("Ctrl+P")
        self.pause_scene_button.setGeometry(0, 0, 100, 50)
        self.pause_scene_button.clicked.connect(
            self.communicate.pause_scene.emit)
        self.resume_scene_button = QPushButton("Resume scene (Ctrl+R)")
        self.resume_scene_button.setShortcut("Ctrl+R")
        self.resume_scene_button.setGeometry(0, 0, 100, 50)
        self.resume_scene_button.clicked.connect(
            self.communicate.resume_scene.emit)
        self.screenshot_button = QPushButton("Screenshot (Ctrl+Shift+P)")
        self.screenshot_button.setShortcut("Ctrl+Shift+P")
        self.screenshot_button.setGeometry(0, 0, 100, 50)
        self.screenshot_button.clicked.connect(self.screenshot)
        self.write_to_python_file_button = QPushButton(
            "Write to Python file (Ctrl+Shift+W)")
        self.write_to_python_file_button.setShortcut("Ctrl+Shift+W")
        self.write_to_python_file_button.setGeometry(0, 0, 100, 50)
        self.write_to_python_file_button.clicked.connect(
            self.write_to_python_file)

        self.menu_bar = QMenuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.open_snip_action = QAction("Open snippet", self)
        self.open_snip_action.setShortcut("Ctrl+O")
        self.open_snip_action.triggered.connect(self.open_snippet)
        self.file_menu.addAction(self.open_snip_action)
        self.open_snip_and_run_action = QAction(
            "Open snippet and run", self)
        self.open_snip_and_run_action.setShortcut("Ctrl+Shift+O")
        self.open_snip_and_run_action.triggered.connect(
            self.open_snippet_and_run)
        self.file_menu.addAction(self.open_snip_and_run_action)
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.add_slider_action = QAction("Add slider", self)
        self.add_slider_action.setShortcut("Ctrl+Shift+1")
        self.add_slider_action.triggered.connect(
            self.add_slider)
        self.edit_menu.addAction(self.add_slider_action)
        self.add_color_widget_action = QAction("Add color widget", self)
        self.add_color_widget_action.setShortcut("Ctrl+Shift+2")
        self.add_color_widget_action.triggered.connect(
            self.add_color_widget)
        self.edit_menu.addAction(self.add_color_widget_action)
        self.add_dropdown_action = QAction("Add dropdown", self)
        self.add_dropdown_action.setShortcut("Ctrl+Shift+3")
        self.add_dropdown_action.triggered.connect(
            self.add_dropdown)
        self.edit_menu.addAction(self.add_dropdown_action)
        self.add_line_editor_widget_action = QAction(
            "Add line editor widget", self)
        self.add_line_editor_widget_action.setShortcut("Ctrl+Shift+4")
        self.add_line_editor_widget_action.triggered.connect(
            self.add_line_editor_widget)
        self.edit_menu.addAction(self.add_line_editor_widget_action)
        self.add_text_editor_widget_action = QAction(
            "Add text editor widget", self)
        self.add_text_editor_widget_action.setShortcut("Ctrl+Shift+5")
        self.add_text_editor_widget_action.triggered.connect(
            self.add_text_editor_widget)
        self.edit_menu.addAction(self.add_text_editor_widget_action)
        self.add_checkbox_widget_action = QAction(
            "Add checkbox widget", self)
        self.add_checkbox_widget_action.setShortcut("Ctrl+Shift+6")
        self.add_checkbox_widget_action.triggered.connect(
            self.add_checkbox_widget)
        self.edit_menu.addAction(self.add_checkbox_widget_action)
        self.add_button_widget_action = QAction(
            "Add button widget", self)
        self.add_button_widget_action.setShortcut("Ctrl+Shift+7")
        self.add_button_widget_action.triggered.connect(
            self.add_button_widget)
        self.edit_menu.addAction(self.add_button_widget_action)
        self.add_position_control_action = QAction(
            "Add position control", self)
        self.add_position_control_action.setShortcut("Ctrl+Shift+8")
        self.add_position_control_action.triggered.connect(
            self.add_position_control)
        self.edit_menu.addAction(self.add_position_control_action)
        self.save_mobject_action = QAction("Save mobject", self)
        self.save_mobject_action.setShortcut("Ctrl+Shift+9")
        self.save_mobject_action.triggered.connect(self.save_mobject)
        self.edit_menu.addAction(self.save_mobject_action)
        self.load_mobject_action = QAction("Load mobject", self)
        self.load_mobject_action.setShortcut("Ctrl+Shift+0")
        self.load_mobject_action.triggered.connect(self.load_mobject)
        self.edit_menu.addAction(self.load_mobject_action)
        self.states_menu = self.menu_bar.addMenu("States")
        self.save_state_action = QAction("Save state", self)
        self.save_state_action.setShortcut("Ctrl+Alt+S")
        self.save_state_action.triggered.connect(self.save_state)
        self.states_menu.addAction(self.save_state_action)
        self.restore_state_action = QAction("Restore state", self)
        self.restore_state_action.setShortcut("Ctrl+Alt+R")
        self.restore_state_action.triggered.connect(self.restore_state)
        self.states_menu.addAction(self.restore_state_action)
        self.remove_state_action = QAction("Remove state", self)
        self.remove_state_action.setShortcut("Ctrl+Alt+D")
        self.remove_state_action.triggered.connect(
            self.remove_state)
        self.states_menu.addAction(self.remove_state_action)
        self.replay_from_state_action = QAction("Replay from state", self)
        self.replay_from_state_action.setShortcut("Ctrl+Alt+P")
        self.replay_from_state_action.triggered.connect(
            self.replay_from_state)
        self.states_menu.addAction(self.replay_from_state_action)

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.menu_bar)
        self.layout_.addWidget(self.enter_your_code_label)
        self.layout_.addWidget(self.code_cell_edit)
        self.layout_.addWidget(self.send_button)
        self.layout_.addWidget(self.end_button)
        self.layout_.addWidget(self.save_snip_button)
        self.layout_.addWidget(self.save_snip_and_run_button)
        self.layout_.addWidget(self.next_slide_button)
        self.layout_.addWidget(self.pause_scene_button)
        self.layout_.addWidget(self.resume_scene_button)
        self.layout_.addWidget(self.screenshot_button)
        self.layout_.addWidget(self.write_to_python_file_button)
        self.controls_widget = QWidget()
        self.controls_scroll = QScrollArea()
        self.controls_scroll.setWidget(self.controls_widget)
        self.controls_scroll.setWidgetResizable(True)
        self.no_controls = QLabel(text="No controls defined")
        self.controls_scroll.setWindowTitle("Manim Studio - Controls")
        self.controls_layout = QGridLayout()
        self.controls_layout.addWidget(self.no_controls)
        self.controls_widget.setLayout(self.controls_layout)
        self.status_bar = QStatusBar()
        self.layout_.addWidget(self.status_bar)
        self.communicate.add_slider_to_editor.connect(
            self.add_slider_to_editor)
        self.communicate.add_color_widget_to_editor.connect(
            self.add_color_widget_to_editor)
        self.communicate.add_dropdown_to_editor.connect(
            self.add_dropdown_to_editor)
        self.communicate.add_line_edit_to_editor.connect(
            self.add_line_editor_widget_to_editor)
        self.communicate.add_text_editor_to_editor.connect(
            self.add_text_editor_to_editor)
        self.communicate.add_checkbox_to_editor.connect(
            self.add_checkbox_to_editor)
        self.communicate.set_control_value.connect(self.set_control_value)
        self.communicate.add_button_to_editor.connect(
            self.add_button_to_editor)
        self.communicate.add_controls_to_client.connect(
            self.add_controls_to_client)
        self.communicate.press_button.connect(self.press_button)
        self.communicate.add_controls_to_clients.connect(
            self.add_controls_to_clients)
        self.communicate.add_position_control_to_editor.connect(
            self.add_position_control_to_editor)
        self.communicate.set_position_control_x.connect(
            lambda name, value: self.controls[name].x_.setValue(float(value)))
        self.communicate.set_position_control_y.connect(
            lambda name, value: self.controls[name].y_.setValue(float(value)))
        self.communicate.set_position_control_z.connect(
            lambda name, value: self.controls[name].z_.setValue(float(value)))
        self.communicate.set_position_control_display_dot.connect(
            lambda name, value: self.controls[name].display_dot_checkbox.setChecked(value == "True"))
        self.communicate.show_in_status_bar.connect(
            self.status_bar.showMessage)
        self.communicate.print_gui.connect(self.print_gui)
        self.setLayout(self.layout_)

    def show(self):
        super().show()
        self.controls_scroll.show()

    def write_to_python_file(self):
        file_name = QFileDialog.getSaveFileName(
            self, "Save Python file", ".", "Python (*.py)")
        if file_name[0]:
            self.scene.python_file_to_write = file_name[0]
            self.replay_from_state()
            return
        alert = QMessageBox(
            text="No file selected.")
        alert.setWindowTitle("No file selected")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.exec()

    def replay_from_state(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Replay from state")
        dialog.layout_ = QVBoxLayout()
        dialog.label = QLabel("Select the state to replay from:")
        dialog.layout_.addWidget(dialog.label)
        dialog.states = QComboBox()
        dialog.states.addItems([state for state in self.scene.states.keys()])
        dialog.layout_.addWidget(dialog.states)
        dialog.ok_button = QPushButton("OK")
        dialog.ok_button.clicked.connect(dialog.close)
        dialog.ok_button.clicked.connect(
            lambda: self.scene.replay_from_state(dialog.states.currentText()))
        dialog.layout_.addWidget(dialog.ok_button)
        dialog.setLayout(dialog.layout_)
        dialog.exec()

    def remove_state(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Remove state")
        dialog.layout_ = QVBoxLayout()
        dialog.label = QLabel("Select the state to remove:")
        dialog.layout_.addWidget(dialog.label)
        dialog.states = QComboBox()
        dialog.states.addItems([state for state in self.scene.states.keys()])
        dialog.layout_.addWidget(dialog.states)
        dialog.ok_button = QPushButton("OK")
        dialog.ok_button.clicked.connect(dialog.close)
        dialog.ok_button.clicked.connect(
            lambda: self.scene.remove_state(dialog.states.currentText()))
        dialog.layout_.addWidget(dialog.ok_button)
        dialog.setLayout(dialog.layout_)
        dialog.exec()

    def screenshot(self):
        file_name = QFileDialog.getSaveFileName(
            self, "Save screenshot", ".", "PNG (*.png)")
        if file_name[0]:
            self.communicate.screenshot.emit(file_name[0])
            dialog = QDialog(self)
            dialog.setWindowTitle("Screenshot")
            dialog.layout_ = QVBoxLayout()
            dialog.label = QLabel("Screenshot saved successfully.")
            dialog.layout_.addWidget(dialog.label)
            dialog.ok_button = QPushButton("OK")
            dialog.ok_button.clicked.connect(dialog.close)
            dialog.layout_.addWidget(dialog.ok_button)
            dialog.setLayout(dialog.layout_)
            dialog.exec()
            return
        alert = QMessageBox(
            text="No file selected.")
        alert.setWindowTitle("No file selected")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.exec()

    def restore_state(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Restore state")
        dialog.layout_ = QVBoxLayout()
        dialog.label = QLabel("Select the state to restore:")
        dialog.layout_.addWidget(dialog.label)
        dialog.states = QComboBox()
        dialog.states.addItems([state for state in self.scene.states.keys()])
        dialog.layout_.addWidget(dialog.states)
        dialog.ok_button = QPushButton("OK")
        dialog.ok_button.clicked.connect(dialog.close)
        dialog.ok_button.clicked.connect(
            lambda: self.scene.restore_state(dialog.states.currentText()))
        dialog.layout_.addWidget(dialog.ok_button)
        dialog.setLayout(dialog.layout_)
        dialog.exec()

    def save_state(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Save state")
        dialog.layout_ = QVBoxLayout()
        dialog.label = QLabel("Enter the name of the state:")
        dialog.layout_.addWidget(dialog.label)
        dialog.name_edit = QLineEdit()
        dialog.name_edit.setPlaceholderText("State name")
        dialog.layout_.addWidget(dialog.name_edit)
        dialog.ok_button = QPushButton("OK")
        dialog.ok_button.clicked.connect(dialog.close)
        dialog.ok_button.clicked.connect(
            lambda: self.scene.save_state(dialog.name_edit.text()))
        dialog.layout_.addWidget(dialog.ok_button)
        dialog.setLayout(dialog.layout_)
        dialog.exec()

    def print_gui(self, text: str):
        dialog = QDialog(self)
        dialog.setWindowTitle("Print")
        dialog.layout_ = QVBoxLayout()
        dialog.text_edit = QTextEdit()
        dialog.text_edit.setReadOnly(True)
        dialog.text_edit.setText(text)
        dialog.layout_.addWidget(dialog.text_edit)
        dialog.ok_button = QPushButton("OK")
        dialog.ok_button.clicked.connect(dialog.close)
        dialog.layout_.addWidget(dialog.ok_button)
        dialog.setLayout(dialog.layout_)
        dialog.exec()

    def add_position_control(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add position control")
        text_edit = QLineEdit(dialog)
        text_edit.setPlaceholderText("Position control name")
        x_label = QLabel("X", dialog)
        x_edit = QDoubleSpinBox(dialog)
        x_edit.setValue(0)
        y_label = QLabel("Y", dialog)
        y_edit = QDoubleSpinBox(dialog)
        y_edit.setValue(0)
        z_label = QLabel("Z", dialog)
        z_edit = QDoubleSpinBox(dialog)
        z_edit.setValue(0)
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        ok_button.clicked.connect(lambda: self.scene.add_position_control_command(
            text_edit.text(), np.array([x_edit.value(), y_edit.value(), z_edit.value()])))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(x_label)
        layout.addWidget(x_edit)
        layout.addWidget(y_label)
        layout.addWidget(y_edit)
        layout.addWidget(z_label)
        layout.addWidget(z_edit)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    def add_position_control_to_editor(self, name: str, default_value: np.ndarray):
        position_control = PositionControl(name, self.scene, default_value)
        self.controls[name] = position_control
        self.controls_layout.addWidget(position_control)
        if self.no_controls.isVisible():
            self.no_controls.hide()
        if self.manim_studio_server is not None:
            self.add_controls_to_clients(
                self.manim_studio_server.clients, {name: position_control})

    def add_controls_to_client(self, s: socket.socket, controls: dict):
        if len(controls) == 0:
            s.sendall(b"no_controls")
            return
        for name, control in controls.items():
            if isinstance(control, Slider):
                s.sendall(f"add_slider {name} {control.value()} {control.minimum()} {control.maximum()} {control.singleStep()}".encode(
                    "utf-8"))
            elif isinstance(control, ColorWidget):
                s.sendall(f"add_color_widget {name} {control.getColor().red()} {control.getColor().green()} {control.getColor().blue()} {control.getColor().alpha()}".encode(
                    "utf-8"))
            elif isinstance(control, DropdownWidget):
                s.sendall(f"add_dropdown {name} {','.join([control.itemText(i) for i in range(control.count())])} {control.currentText()}".encode(
                    "utf-8"))
            elif isinstance(control, LineEditorWidget):
                s.sendall(f"add_line_editor_widget {name} {control.text()}".encode(
                    "utf-8"))
            elif isinstance(control, TextEditorWidget):
                s.sendall(f"add_text_editor_widget {name} {control.toPlainText()}".encode(
                    "utf-8"))
            elif isinstance(control, CheckboxWidget):
                s.sendall(f"add_checkbox {name} {control.isChecked()}".encode(
                    "utf-8"))
            elif isinstance(control, Button):
                s.sendall(f"add_button {name}".encode(
                    "utf-8"))
            elif isinstance(control, PositionControl):
                s.sendall(f"add_position_control {name} {control.x_.value()} {control.y_.value()} {control.z_.value()}".encode(
                    "utf-8"))

    def add_controls_to_clients(self, clients: list[socket.socket], controls: dict):
        for client in clients:
            self.add_controls_to_client(client, controls)

    def press_button(self, name: str):
        self.communicate.update_scene.emit(self.controls[name].callback)

    def add_button_widget(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add button widget")
        text_edit = QLineEdit(dialog)
        text_edit.setPlaceholderText("Button widget name")
        callback_label = QLabel("Enter the button's callback below:", dialog)
        callback_edit = CodeEdit(dialog)
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        ok_button.clicked.connect(lambda: self.scene.add_button_command(
            text_edit.text(), callback_edit.text()))

        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(callback_label)
        layout.addWidget(callback_edit)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    def add_button_to_editor(self, name: str, callback: str):
        button = Button(callback, self.communicate, text=name)
        self.controls[name] = button
        self.controls_layout.addWidget(button)
        if self.no_controls.isVisible():
            self.no_controls.hide()
        if self.manim_studio_server is not None:
            self.add_controls_to_clients(
                self.manim_studio_server.clients, {name: button})

    @pyqtSlot(str, str)
    def set_control_value(self, name: str, value: str):
        control = self.controls.get(name)
        if control is None:
            alert = QMessageBox()
            alert.setText(f"Control {name} not found")
            alert.exec()
            return
        if isinstance(control, Slider):
            control.setValue(int(value))
        elif isinstance(control, ColorWidget):
            value = value.split(",")
            control.setCurrentColor(QColor(int(value[0]), int(
                value[1]), int(value[2]), int(value[3])))
        elif isinstance(control, DropdownWidget):
            control.setCurrentText(value)
        elif isinstance(control, LineEditorWidget):
            control.setText(value)
        elif isinstance(control, TextEditorWidget):
            control.setText(value)
        elif isinstance(control, CheckboxWidget):
            control.setChecked(value == "True")
        elif isinstance(control, Button):
            control.clicked.disconnect()
            control.clicked.connect(
                lambda: self.communicate.update_scene.emit(value))
        elif isinstance(control, PositionControl):
            value = value.split(",")
            control.x_.setValue(float(value[0]))
            control.y_.setValue(float(value[1]))
            control.z_.setValue(float(value[2]))

    def save_mobject(self):
        self.communicate.save_mobject.emit()

    def load_mobject(self):
        self.communicate.load_mobject.emit()

    def add_text_editor_widget(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add text editor widget")
        name_edit = QLineEdit(dialog)
        name_edit.setPlaceholderText("Text editor widget name")
        default_value_label = QLabel("Enter the default text below:", dialog)
        default_value_edit = CodeEdit(dialog)
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        ok_button.clicked.connect(lambda: self.scene.add_text_editor_command(
            name_edit.text(), default_value_edit.text()))
        layout = QVBoxLayout()
        layout.addWidget(name_edit)
        layout.addWidget(default_value_label)
        layout.addWidget(default_value_edit)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    @pyqtSlot(str, bool)
    def add_checkbox_to_editor(self, name: str, default_value: bool):
        label = QLabel(text=name)
        checkbox = CheckboxWidget(name)
        checkbox.setChecked(default_value)
        self.controls[name] = checkbox
        setattr(self.scene, name, checkbox.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(checkbox)
        if self.no_controls.isVisible():
            self.no_controls.hide()
        if self.manim_studio_server is not None:
            self.add_controls_to_clients(
                self.manim_studio_server.clients, {name: checkbox})

    @pyqtSlot(str, str)
    def add_text_editor_to_editor(self, name: str, default_value: str):
        label = QLabel(text=name)
        text_editor_widget = TextEditorWidget(name)
        text_editor_widget.setText(default_value)
        self.controls[name] = text_editor_widget
        self.scene.value_trackers[name] = text_editor_widget.value_tracker
        setattr(self.scene, name, text_editor_widget.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(text_editor_widget)
        if self.no_controls.isVisible():
            self.no_controls.hide()
        if self.manim_studio_server is not None:
            self.add_controls_to_clients(
                self.manim_studio_server.clients, {name: text_editor_widget})

    def add_checkbox_widget(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add checkbox widget")
        text_edit = QLineEdit(dialog)
        text_edit.setPlaceholderText("Checkbox widget name")
        default_value_edit = QCheckBox(dialog)
        default_value_edit.setText("Is default value True?")
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        ok_button.clicked.connect(lambda: self.scene.add_checkbox_command(
            text_edit.text(), default_value_edit.isChecked()))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(default_value_edit)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    def add_dropdown(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add dropdown")
        text_edit = QLineEdit(dialog)
        text_edit.setPlaceholderText("Dropdown name")
        options_edit = QLineEdit(dialog)
        options_edit.setPlaceholderText("Dropdown options")
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        default_value_edit = QLineEdit(dialog)
        default_value_edit.setPlaceholderText("Default value")
        ok_button.clicked.connect(lambda: self.scene.add_dropdown_command(
            text_edit.text(), options_edit.text().split(","), default_value_edit.text()))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(options_edit)
        layout.addWidget(default_value_edit)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    def add_line_editor_widget(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add line editor widget")
        text_edit = QLineEdit(dialog)
        text_edit.setPlaceholderText("Line editor widget name")
        default_value_edit = QLineEdit(dialog)
        default_value_edit.setPlaceholderText("Default value")
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        ok_button.clicked.connect(lambda: self.scene.add_line_edit_command(
            text_edit.text(), default_value_edit.text()))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(default_value_edit)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    @pyqtSlot(str, str)
    def add_line_editor_widget_to_editor(self, name: str, default_value: str):
        label = QLabel(text=name)
        line_editor_widget = LineEditorWidget(name)
        line_editor_widget.setText(default_value)
        self.controls[name] = line_editor_widget
        self.scene.value_trackers[name] = line_editor_widget.value_tracker
        setattr(self.scene, name, line_editor_widget.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(line_editor_widget)
        if self.no_controls.isVisible():
            self.no_controls.hide()
        if self.manim_studio_server is not None:
            self.add_controls_to_clients(
                self.manim_studio_server.clients, {name: line_editor_widget})

    def send_code(self):
        self.communicate.update_scene.emit(self.code_cell_edit.text())
        self.code_cell_edit.clear()

    def add_slider(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add slider")
        text_edit = QLineEdit(dialog)
        text_edit.setPlaceholderText("Slider name")
        default_value_edit = QLineEdit(dialog)
        default_value_edit.setValidator(QIntValidator(
            -2147483648, 2147483647))
        default_value_edit.setPlaceholderText("Default value")
        min_value_edit = QLineEdit(dialog)
        min_value_edit.setValidator(QIntValidator(
            -2147483648, 2147483647))
        min_value_edit.setPlaceholderText("Minimum value")
        max_value_edit = QLineEdit(dialog)
        max_value_edit.setValidator(QIntValidator(
            -2147483648, 2147483647))
        max_value_edit.setPlaceholderText("Maximum value")
        step_value_edit = QLineEdit(dialog)
        step_value_edit.setValidator(QIntValidator(
            -2147483648, 2147483647))
        step_value_edit.setPlaceholderText("Step value")
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        ok_button.clicked.connect(lambda: self.scene.add_slider_command(
            text_edit.text(), default_value_edit.text(), min_value_edit.text(), max_value_edit.text(), step_value_edit.text()))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(default_value_edit)
        layout.addWidget(min_value_edit)
        layout.addWidget(max_value_edit)
        layout.addWidget(step_value_edit)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    def add_color_widget(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add color widget")
        text_edit = QLineEdit(dialog)
        text_edit.setPlaceholderText("Color widget name")
        default_r_edit = QLineEdit(dialog)
        default_r_edit.setValidator(QIntValidator(
            0, 255))
        default_r_edit.setPlaceholderText("Default red value")
        default_g_edit = QLineEdit(dialog)
        default_g_edit.setValidator(QIntValidator(
            0, 255))
        default_g_edit.setPlaceholderText("Default green value")
        default_b_edit = QLineEdit(dialog)
        default_b_edit.setValidator(QIntValidator(
            0, 255))
        default_b_edit.setPlaceholderText("Default blue value")
        default_a_edit = QLineEdit(dialog)
        default_a_edit.setValidator(QIntValidator(
            0, 255))
        default_a_edit.setPlaceholderText("Default alpha value")
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        ok_button.clicked.connect(lambda: self.scene.add_color_widget_command(
            text_edit.text(), np.array([int(default_r_edit.text()), int(default_g_edit.text()), int(default_b_edit.text()), int(default_a_edit.text())])))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(default_r_edit)
        layout.addWidget(default_g_edit)
        layout.addWidget(default_b_edit)
        layout.addWidget(default_a_edit)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    @pyqtSlot(str, np.ndarray)
    def add_color_widget_to_editor(self, name: str, default_value: np.ndarray):
        default_value = np.array(default_value)
        label = QLabel(text=name)
        color_widget = ColorWidget()
        color_widget.setCurrentColor(QColor(
            default_value[0], default_value[1], default_value[2], default_value[3]))
        self.controls[name] = color_widget
        self.scene.value_trackers[name] = color_widget.color_tracker
        setattr(self.scene, name, color_widget.color_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(color_widget)
        if self.no_controls.isVisible():
            self.no_controls.hide()
        if self.manim_studio_server is not None:
            self.add_controls_to_clients(
                self.manim_studio_server.clients, {name: color_widget})

    @pyqtSlot(str, str, str, str, str)
    def add_slider_to_editor(self, name: str, default_value: str, min_value: str, max_value: str, step_value: str):
        label = QLabel(text=name)
        slider = Slider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_value))
        slider.setMaximum(int(max_value))
        slider.setValue(int(default_value))
        slider.setSingleStep(int(step_value))
        self.controls[name] = slider
        self.scene.value_trackers[name] = slider.value_tracker
        setattr(self.scene, name, slider.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(slider)
        if self.no_controls.isVisible():
            self.no_controls.hide()
        if self.manim_studio_server is not None:
            self.add_controls_to_clients(
                self.manim_studio_server.clients, {name: slider})

    @pyqtSlot(str, list, str)
    def add_dropdown_to_editor(self, name: str, options: list[str], default_value: str):
        label = QLabel(text=name)
        dropdown = DropdownWidget()
        dropdown.addItems(options)
        dropdown.setCurrentText(default_value)
        self.controls[name] = dropdown
        self.scene.value_trackers[name] = dropdown.value_tracker
        setattr(self.scene, name, dropdown.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(dropdown)
        if self.no_controls.isVisible():
            self.no_controls.hide()
        if self.manim_studio_server is not None:
            self.add_controls_to_clients(
                self.manim_studio_server.clients, {name: dropdown})

    def save_snippet(self):
        self.communicate.save_snippet.emit(self.code_cell_edit.toPlainText())

    def save_snippet_command(self, code: str):
        controls_dialog = ControlDialog(self.controls)
        add_controls, controls_toggle = controls_dialog.exec_and_return()
        file_ = QFileDialog.getSaveFileName(
            self, "Save snippet", ".", "Manim Studio Snippet (*.mss)")
        if file_[0]:
            self.ready_to_save = True
            with open(file_[0], "w", encoding="utf-8") as f:
                f.write(code)
            if add_controls is True:
                controls = {k: v for k, v in self.controls.items()
                            if k in controls_toggle.keys() and controls_toggle[k] is True}

                def get_tup(v):
                    if isinstance(v, Slider):
                        return ("Slider", v.value(), v.minimum(), v.maximum(), v.singleStep())
                    elif isinstance(v, ColorWidget):
                        return ("ColorWidget", list(v.currentColor().getRgb()))
                    elif isinstance(v, DropdownWidget):
                        return ("DropdownWidget", [v.itemText(i) for i in range(v.count())], v.currentText())
                    elif isinstance(v, LineEditorWidget):
                        return ("LineEditorWidget", v.text())
                    elif isinstance(v, TextEditorWidget):
                        return ("TextEditorWidget", v.toPlainText())
                    elif isinstance(v, CheckboxWidget):
                        return ("CheckboxWidget", v.isChecked())
                    elif isinstance(v, Button):
                        return ("Button", v.callback)
                    elif isinstance(v, PositionControl):
                        return ("PositionControl", v.x_.value(), v.y_.value(), v.z_.value(), v.display_dot_checkbox.isChecked())

                controls = {k: get_tup(v) for k, v in controls.items()}
                with open(f"{file_[0]}.controls", "wb") as f:
                    pickle.dump(controls, f)
            else:
                if Path(f"{file_[0]}.controls").exists():
                    Path(f"{file_[0]}.controls").unlink()

    def save_snippet_and_run(self):
        self.save_snippet()
        self.send_code()

    def open_snippet(self):
        file_ = QFileDialog.getOpenFileName(
            self, "Open snippet", ".", "Manim Studio Snippet (*.mss)")
        if file_[0]:
            with open(file_[0], "r", encoding="utf-8") as f:
                self.code_cell_edit.setText(
                    f"{self.code_cell_edit.toPlainText()}\n{f.read()}")
            if Path(f"{file_[0]}.controls").exists():
                with open(f"{file_[0]}.controls", "rb") as f:
                    controls = pickle.load(f)
                for name, control in controls.items():
                    if name in self.controls.keys():
                        continue
                    if control[0] == "Slider":
                        self.add_slider_to_editor(
                            name, control[1], control[2], control[3], control[4])
                    elif control[0] == "ColorWidget":
                        self.add_color_widget_to_editor(
                            name, np.array(control[1]))
                    elif control[0] == "DropdownWidget":
                        self.add_dropdown_to_editor(
                            name, control[1], control[2])
                    elif control[0] == "LineEditorWidget":
                        self.add_line_editor_widget_to_editor(
                            name, control[1])
                    elif control[0] == "TextEditorWidget":
                        self.add_text_editor_to_editor(
                            name, control[1])
                    elif control[0] == "CheckboxWidget":
                        self.add_checkbox_to_editor(
                            name, control[1])
                    elif control[0] == "Button":
                        self.add_button_to_editor(
                            name, control[1])
                    elif control[0] == "PositionControl":
                        self.add_position_control_to_editor(
                            name, np.array([control[1], control[2], control[3]]))
        else:
            alert = QMessageBox(
                text="No file selected.")
            alert.setWindowTitle("No file selected")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.exec()

    def open_snippet_and_run(self):
        self.open_snippet()
        self.send_code()

    def next_slide(self):
        if self.scene.freeze is False:
            alert = QMessageBox(
                text="The scene is not paused.")
            alert.setWindowTitle("Scene not paused")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.exec()
            return
        self.scene.freeze = False

    def end_scene(self):
        self.communicate.end_scene.emit()
