from manim_studio.communicate import Communicate
from manim_studio.code_edit import CodeEdit
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QStatusBar,
    QMenuBar,
    QDialog,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QTextEdit
)
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from manim_studio.controls.slider_control import SliderControl
from manim_studio.controls.text_control import TextControl
from manim_studio.controls.line_control import LineControl
from manim_studio.controls.color_control import ColorControl
from manim_studio.controls.dropdown_control import DropdownControl
from manim_studio.controls.checkbox_control import CheckboxControl
from manim_studio.controls.spin_box_control import SpinBoxControl
from manim_studio.controls.file_control import FileControl
from manim_studio.controls.position_control import PositionControl
from manim_studio.controls.button import Button
from manim_studio.controls_widget import ControlsWidget
from manim_studio.live_scene import LiveScene
from manim_studio.mobject_picker import MobjectPicker, RefreshDropdownVGroupButton
from manim_studio.animation_picker import AnimationPicker
import numpy as np
import time
import dill as pickle


class EditorWidget(QWidget):
    def __init__(self, communicate: Communicate, controls_widget: ControlsWidget, scene: LiveScene, from_project: str):
        super().__init__()
        self.setWindowTitle("Manim Studio Editor")
        self.controls_widget = controls_widget
        self.setWindowTitle("Manim Studio")
        self.communicate = communicate
        self.scene = scene
        self.communicate.print_gui.connect(self.print_gui)
        self.states = ["first"]
        self.controls = {}
        self.from_project = from_project
        self.init_ui()
        self.communicate.save_project.connect(self.save_controls)
        self.communicate.load_project.connect(self.load_controls)

    def save_controls(self):
        while not hasattr(self.scene, f"_LiveScene__file_name"):
            time.sleep(0)
        file_name = getattr(
            self.scene, f"_LiveScene__file_name")
        if not file_name:
            return
        controls = [control.to_dict() for control in self.controls.values()]
        with open(file_name + "_controls.pkl", "wb") as f:
            pickle.dump(controls, f)

    def load_controls(self):
        with open(self.from_project + "_controls.pkl", "rb") as f:
            controls = pickle.load(f)
        for control in controls:
            self.add_custom_control_command(control["name"], eval(control["class"]).from_dict(
                self.communicate, control))

    def print_gui(self, text: str):
        dialog = QDialog(self)
        dialog.setWindowTitle("Print GUI")
        dialog.setLayout(QVBoxLayout(dialog))
        text_edit = QTextEdit(text)
        text_edit.setReadOnly(True)
        dialog.layout().addWidget(text_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def init_ui(self):
        self.init_basic_ui()
        self.init_menu_bar()
        self.init_code_edit()
        self.init_buttons()
        self.init_status_bar()

    def init_menu_bar(self):
        self.menu_bar = QMenuBar()
        self.layout().setMenuBar(self.menu_bar)
        self.file_menu = self.menu_bar.addMenu("File")
        self.save_manim_studio_project_action = self.file_menu.addAction(
            "Save Manim Studio Project")
        self.save_manim_studio_project_action.setShortcut("Ctrl+S")
        self.save_manim_studio_project_action.triggered.connect(
            self.communicate.save_project.emit)
        self.save_to_python_action = self.file_menu.addAction(
            "Save to Python Manim File")
        self.save_to_python_action.setShortcut("Ctrl+Shift+S")
        self.save_to_python_action.triggered.connect(self.save_to_python)
        self.controls_menu = self.menu_bar.addMenu("Controls")
        self.add_slider_action = self.controls_menu.addAction("Add Slider")
        self.add_slider_action.triggered.connect(self.add_slider)
        self.add_text_box_action = self.controls_menu.addAction("Add Text Box")
        self.add_text_box_action.triggered.connect(self.add_text_box)
        self.add_line_box_action = self.controls_menu.addAction("Add Line Box")
        self.add_line_box_action.triggered.connect(self.add_line_box)
        self.add_color_picker_action = self.controls_menu.addAction(
            "Add Color Picker")
        self.add_color_picker_action.triggered.connect(self.add_color_picker)
        self.add_dropdown_action = self.controls_menu.addAction(
            "Add Dropdown")
        self.add_dropdown_action.triggered.connect(self.add_dropdown)
        self.add_checkbox_action = self.controls_menu.addAction(
            "Add Checkbox")
        self.add_checkbox_action.triggered.connect(self.add_checkbox)
        self.add_spin_box_action = self.controls_menu.addAction(
            "Add Spin Box")
        self.add_spin_box_action.triggered.connect(self.add_spin_box)
        self.add_file_selector_action = self.controls_menu.addAction(
            "Add File Selector")
        self.add_file_selector_action.triggered.connect(self.add_file_selector)
        self.add_position_control_action = self.controls_menu.addAction(
            "Add Position Control")
        self.add_position_control_action.triggered.connect(
            self.add_position_control)
        self.add_button_action = self.controls_menu.addAction("Add Button")
        self.add_button_action.triggered.connect(self.add_button)
        self.states_menu = self.menu_bar.addMenu("States")
        self.save_state_action = self.states_menu.addAction("New State")
        self.save_state_action.setShortcut("Ctrl+Shift+S")
        self.save_state_action.triggered.connect(self.save_state)
        self.restore_state_action = self.states_menu.addAction("Restore State")
        self.restore_state_action.setShortcut("Ctrl+Shift+R")
        self.restore_state_action.triggered.connect(self.restore_state)
        self.remove_state_action = self.states_menu.addAction("Remove State")
        self.remove_state_action.setShortcut("Ctrl+Shift+D")
        self.remove_state_action.triggered.connect(self.remove_state)

    def init_basic_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def init_code_edit(self):
        self.code_label = QLabel("Enter your Python code here:")
        self.layout().addWidget(self.code_label)
        self.code_edit = CodeEdit()
        self.layout().addWidget(self.code_edit)

    def init_buttons(self):
        self.run_button = QPushButton("Run (Ctrl+Return)")
        self.run_button.setShortcut("Ctrl+Return")
        self.run_button.clicked.connect(self.run)
        self.layout().addWidget(self.run_button)
        self.finish_button = QPushButton("Finish (Ctrl+Q)")
        self.finish_button.setShortcut("Ctrl+Q")
        self.finish_button.clicked.connect(self.finish)
        self.layout().addWidget(self.finish_button)
        self.save_mobject_button = QPushButton("Save Mobject")
        self.save_mobject_button.clicked.connect(
            self.communicate.save_mobject.emit)
        self.layout().addWidget(self.save_mobject_button)
        self.load_mobject_button = QPushButton("Load Mobject")
        self.load_mobject_button.clicked.connect(
            self.communicate.load_mobject.emit)
        self.layout().addWidget(self.load_mobject_button)
        self.mobject_picker = MobjectPicker(self)
        self.show_mobject_picker_button = QPushButton("Show Mobject Picker")
        self.show_mobject_picker_button.clicked.connect(
            self.mobject_picker.show)
        self.layout().addWidget(self.show_mobject_picker_button)
        self.show_animation_picker_button = QPushButton(
            "Show Animation Picker")
        self.animation_picker = AnimationPicker(self)
        self.show_animation_picker_button.clicked.connect(
            self.animation_picker.show)
        self.layout().addWidget(self.show_animation_picker_button)

    def init_status_bar(self):
        self.status_bar = QStatusBar()
        self.layout().addWidget(self.status_bar)

    def run(self):
        self.communicate.update_scene.emit(self.code_edit.toPlainText())

    def finish(self):
        self.communicate.update_scene.emit("raise EndSceneEarlyException()")
        self.status_bar.showMessage("Finished.")

    def save_to_python(self):
        self.communicate.save_to_python.emit()

    def save_state(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Save State")
        dialog.setLayout(QVBoxLayout(dialog))
        label = QLabel("Enter the name of the state:")
        dialog.layout().addWidget(label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.save_state_command(name_edit.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def save_state_command(self, name: str):
        if name == "temp":
            self.communicate.print_gui.emit(
                "Cannot save a state with the name 'temp'. It's reserved for internal use.")
            return
        self.communicate.save_state.emit(name)
        self.states.append(name)

    def restore_state(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Restore State")
        dialog.setLayout(QVBoxLayout(dialog))
        label = QLabel("Enter the name of the state:")
        dialog.layout().addWidget(label)
        name_edit = QComboBox()
        dialog.layout().addWidget(name_edit)
        name_edit.addItems(self.states)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.restore_state_command(name_edit.currentText()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def restore_state_command(self, name: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please select a state to restore.")
            return
        self.communicate.restore_state.emit(name)

    def remove_state(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Remove State")
        dialog.setLayout(QVBoxLayout(dialog))
        label = QLabel("Enter the name of the state:")
        dialog.layout().addWidget(label)
        name_edit = QComboBox()
        name_edit.addItems(
            [state for state in self.states if state != "first"])
        dialog.layout().addWidget(name_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.remove_state_command(name_edit.currentText()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def remove_state_command(self, name: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please select a state to remove.")
            return
        self.communicate.remove_state.emit(name)
        self.states.remove(name)

    def add_slider(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Slider")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the slider:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        min_label = QLabel("Enter the minimum value of the slider:")
        dialog.layout().addWidget(min_label)
        min_edit = QLineEdit()
        min_edit.setValidator(QIntValidator())
        dialog.layout().addWidget(min_edit)
        max_label = QLabel("Enter the maximum value of the slider:")
        dialog.layout().addWidget(max_label)
        max_edit = QLineEdit()
        max_edit.setValidator(QIntValidator())
        dialog.layout().addWidget(max_edit)
        step_label = QLabel("Enter the step of the slider:")
        dialog.layout().addWidget(step_label)
        step_edit = QLineEdit()
        step_edit.setValidator(QIntValidator())
        dialog.layout().addWidget(step_edit)
        default_label = QLabel("Enter the default value of the slider:")
        dialog.layout().addWidget(default_label)
        default_edit = QLineEdit()
        default_edit.setValidator(QIntValidator())
        dialog.layout().addWidget(default_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_slider_command(name_edit.text(), min_edit.text(), max_edit.text(), step_edit.text(), default_edit.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_slider_command(self, name: str, min_: str, max_: str, step: str, default: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the slider.")
            return
        if min_ == "":
            self.communicate.print_gui.emit(
                "Please enter a minimum value for the slider.")
            return
        if max_ == "":
            self.communicate.print_gui.emit(
                "Please enter a maximum value for the slider.")
            return
        if step == "":
            self.communicate.print_gui.emit(
                "Please enter a step for the slider.")
            return
        if default == "":
            self.communicate.print_gui.emit(
                "Please enter a default value for the slider.")
            return
        if int(min_) > int(max_):
            self.communicate.print_gui.emit(
                "The minimum value cannot be greater than the maximum value.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        slider = SliderControl(
            self.communicate, name, (int(min_), int(max_)), int(step), int(default))
        self.controls_widget.add_controls(slider)
        self.communicate.add_value_tracker.emit(
            name, slider.value_tracker)
        self.controls[name] = slider
        return slider

    def add_text_box(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Text Box")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the text box:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_text_box_command(name_edit.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_text_box_command(self, name: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the text box.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        text_box = TextControl(self.communicate, name)
        self.controls_widget.add_controls(text_box)
        self.communicate.add_value_tracker.emit(
            name, text_box.value_tracker)
        self.controls[name] = text_box
        return text_box

    def add_line_box(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Line Box")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the line box:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_line_box_command(name_edit.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_line_box_command(self, name: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the line box.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        line_box = LineControl(self.communicate, name)
        self.controls_widget.add_controls(line_box)
        self.communicate.add_value_tracker.emit(
            name, line_box.value_tracker)
        self.controls[name] = line_box
        return line_box

    def add_color_picker(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Color Picker")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the color picker:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_color_picker_command(name_edit.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_color_picker_command(self, name: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the color picker.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        color_picker = ColorControl(self.communicate, name)
        self.controls_widget.add_controls(color_picker)
        self.communicate.add_value_tracker.emit(
            name, color_picker.value_tracker)
        self.controls[name] = color_picker
        return color_picker

    def add_dropdown(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Dropdown")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the dropdown:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        dialog.options = []
        dialog.option_edit = QLineEdit()
        dialog.option_edit.setPlaceholderText("Enter your option here")
        dialog.layout().addWidget(dialog.option_edit)
        add_option_button = QPushButton("Add Option")
        dialog.layout().addWidget(add_option_button)
        add_option_button.clicked.connect(
            lambda: self.add_option_command(dialog))
        your_current_options_label = QLabel("Your current options:")
        dialog.layout().addWidget(your_current_options_label)
        dialog.options_label = QLabel("")
        dialog.layout().addWidget(dialog.options_label)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_dropdown_command(name_edit.text(), dialog.options))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_option_command(self, dialog: QDialog):
        if dialog.option_edit.text() == "":
            self.communicate.print_gui.emit(
                "Please enter an option.")
            return
        dialog.options.append(dialog.option_edit.text())
        dialog.option_edit.setText("")
        dialog.options_label.setText("\n".join(dialog.options))

    def add_dropdown_command(self, name: str, options: list[str]):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the dropdown.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        dropdown = DropdownControl(self.communicate, name, options)
        self.controls_widget.add_controls(dropdown)
        self.communicate.add_value_tracker.emit(
            name, dropdown.value_tracker)
        self.communicate.add_value_tracker.emit(
            name + "_items", dropdown.list_value_tracker)
        self.controls[name] = dropdown
        return dropdown

    def add_checkbox(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Checkbox")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the checkbox:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        default_checkbox = QCheckBox()
        default_checkbox.setText("Default is true or false?")
        default_checkbox.setChecked(False)
        dialog.layout().addWidget(default_checkbox)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_checkbox_command(name_edit.text(), default_checkbox.isChecked()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_checkbox_command(self, name: str, default: bool):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the checkbox.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        checkbox = CheckboxControl(self.communicate, name, default)
        self.controls_widget.add_controls(checkbox)
        self.communicate.add_value_tracker.emit(
            name, checkbox.value_tracker)
        self.controls[name] = checkbox
        return checkbox

    def add_spin_box(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Spin Box")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the spin box:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        min_label = QLabel("Enter the minimum value of the spin box:")
        dialog.layout().addWidget(min_label)
        min_edit = QLineEdit()
        min_edit.setValidator(QDoubleValidator())
        dialog.layout().addWidget(min_edit)
        max_label = QLabel("Enter the maximum value of the spin box:")
        dialog.layout().addWidget(max_label)
        max_edit = QLineEdit()
        max_edit.setValidator(QDoubleValidator())
        dialog.layout().addWidget(max_edit)
        default_label = QLabel("Enter the default value of the spin box:")
        dialog.layout().addWidget(default_label)
        default_edit = QLineEdit()
        default_edit.setValidator(QDoubleValidator())
        dialog.layout().addWidget(default_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_spin_box_command(name_edit.text(), min_edit.text(), max_edit.text(), default_edit.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_spin_box_command(self, name: str, min_: str, max_: str, default: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the spin box.")
            return
        if min_ == "":
            self.communicate.print_gui.emit(
                "Please enter a minimum value for the spin box.")
            return
        if max_ == "":
            self.communicate.print_gui.emit(
                "Please enter a maximum value for the spin box.")
            return
        if default == "":
            self.communicate.print_gui.emit(
                "Please enter a default value for the spin box.")
            return
        if float(min_) > float(max_):
            self.communicate.print_gui.emit(
                "The minimum value cannot be greater than the maximum value.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        spin_box = SpinBoxControl(self.communicate, name, float(
            default), float(min_), float(max_))
        self.controls_widget.add_controls(spin_box)
        self.communicate.add_value_tracker.emit(
            name, spin_box.value_tracker)
        self.controls[name] = spin_box
        return spin_box

    def add_file_selector(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add File Selector")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the file selector:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_file_selector_command(name_edit.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_file_selector_command(self, name: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the file selector.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        file_selector = FileControl(self.communicate, name)
        self.controls_widget.add_controls(file_selector)
        self.communicate.add_value_tracker.emit(
            name, file_selector.value_tracker)
        self.controls[name] = file_selector
        return file_selector

    def add_position_control(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Position Control")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the position control:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        x_label = QLabel("Enter the x value of the position control:")
        dialog.layout().addWidget(x_label)
        x_edit = QLineEdit()
        x_edit.setValidator(QDoubleValidator())
        dialog.layout().addWidget(x_edit)
        y_label = QLabel("Enter the y value of the position control:")
        dialog.layout().addWidget(y_label)
        y_edit = QLineEdit()
        y_edit.setValidator(QDoubleValidator())
        dialog.layout().addWidget(y_edit)
        z_label = QLabel("Enter the z value of the position control:")
        dialog.layout().addWidget(z_label)
        z_edit = QLineEdit()
        z_edit.setValidator(QDoubleValidator())
        dialog.layout().addWidget(z_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_position_control_command(name_edit.text(), x_edit.text(), y_edit.text(), z_edit.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_position_control_command(self, name: str, x: str, y: str, z: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the position control.")
            return
        if x == "":
            self.communicate.print_gui.emit(
                "Please enter an x value for the position control.")
            return
        if y == "":
            self.communicate.print_gui.emit(
                "Please enter a y value for the position control.")
            return
        if z == "":
            self.communicate.print_gui.emit(
                "Please enter a z value for the position control.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        position_control = PositionControl(
            self.communicate, name, np.array([float(x), float(y), float(z)]))
        self.controls_widget.add_controls(position_control)
        self.communicate.add_value_tracker.emit(
            name, position_control.value_tracker)
        self.controls[name] = position_control
        return position_control

    def add_button(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Button")
        dialog.setLayout(QVBoxLayout(dialog))
        name_label = QLabel("Enter the name of the button:")
        dialog.layout().addWidget(name_label)
        name_edit = QLineEdit()
        dialog.layout().addWidget(name_edit)
        callback_label = QLabel("Enter the callback of the button:")
        dialog.layout().addWidget(callback_label)
        callback_edit = CodeEdit()
        dialog.layout().addWidget(callback_edit)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_button_command(name_edit.text(), callback_edit.toPlainText()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_button_command(self, name: str, callback: str):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the button.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        button = Button(self.communicate, name, callback)
        self.controls_widget.add_controls(button)
        self.controls[name] = button
        return button

    def add_custom_control_command(self, name: str, control: QWidget):
        self.controls_widget.add_controls(control)
        self.controls[name] = control
        return control
