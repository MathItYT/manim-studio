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
    QTextEdit,
    QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QDoubleValidator, QKeyEvent
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
from manim import Mobject


class LiveSceneState:
    def __init__(self, dict_: dict):
        self.scene_dict = dict_


class InteractiveMobjectsControl(QWidget):
    def __init__(self, communicate: Communicate, editor_widget: QWidget):
        super().__init__()
        self.communicate = communicate
        self.editor_widget = editor_widget
        self.init_ui()

    def init_ui(self):
        self.interactive_mobjects = []
        self.setLayout(QVBoxLayout(self))
        self.label = QLabel(
            "Select a mobject to make it interactive (or disable interactivity):")
        self.layout().addWidget(self.label)
        self.dropdown = QComboBox()
        self.layout().addWidget(self.dropdown)
        self.dropdown.addItems(
            [mob for mob in dir(self.editor_widget.scene) if isinstance(getattr(self.editor_widget.scene, mob), Mobject)])
        self.refresh_button = QPushButton("Refresh Mobject list")
        self.layout().addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self.refresh)
        self.add_to_interactive_mobjects_button = QPushButton(
            "Add to interactive mobjects")
        self.layout().addWidget(self.add_to_interactive_mobjects_button)
        self.add_to_interactive_mobjects_button.clicked.connect(
            self.add_to_interactive_mobjects)
        self.remove_from_interactive_mobjects_button = QPushButton(
            "Remove from interactive mobjects")
        self.layout().addWidget(self.remove_from_interactive_mobjects_button)
        self.remove_from_interactive_mobjects_button.clicked.connect(
            self.remove_from_interactive_mobjects)
        self.current_interactive_mobjects_label = QLabel(
            "Current interactive mobjects:")
        self.layout().addWidget(self.current_interactive_mobjects_label)

    def refresh(self):
        self.dropdown.clear()
        self.dropdown.addItems(
            [mob for mob in dir(self.editor_widget.scene) if isinstance(getattr(self.editor_widget.scene, mob), Mobject)])

    def add_to_interactive_mobjects(self):
        self.communicate.add_to_interactive_mobjects.emit(
            self.dropdown.currentText())
        if self.dropdown.currentText() not in self.interactive_mobjects:
            self.interactive_mobjects.append(self.dropdown.currentText())
        self.current_interactive_mobjects_label.setText(
            "Current interactive mobjects:\n" + "\n".join(self.interactive_mobjects))

    def remove_from_interactive_mobjects(self):
        self.communicate.remove_from_interactive_mobjects.emit(
            self.dropdown.currentText())
        if self.dropdown.currentText() in self.interactive_mobjects:
            self.interactive_mobjects.remove(self.dropdown.currentText())
        self.current_interactive_mobjects_label.setText(
            "Current interactive mobjects:\n" +
            "\n".join(self.interactive_mobjects)
            if self.interactive_mobjects else "Current interactive mobjects:")


class EditorWidget(QWidget):
    def __init__(
        self,
        communicate: Communicate,
        controls_widget: ControlsWidget,
        scene: LiveScene
    ):
        super().__init__()
        self.communicate = communicate
        self.communicate.print_gui.connect(self.print_gui)
        self.communicate.save_state.connect(self.save_state)
        self.communicate.undo_state.connect(self.undo_state)
        self.communicate.redo_state.connect(self.redo_state)
        self.scene = scene
        self.states = []
        self.states_to_redo = []
        self.setWindowTitle("Manim Studio Editor")
        self.controls_widget = controls_widget
        self.setWindowTitle("Manim Studio")
        self.controls = {}
        self.init_ui()
    
    def save_state(self):
        self.states.append(LiveSceneState(self.scene.__dict__.copy()))
        self.states_to_redo = []
    
    def undo_state(self):
        if len(self.states) == 1:
            self.print_gui("There's nothing to undo.")
            return
        self.states_to_redo.append(self.states.pop())
        self.scene.__dict__ = self.states[-1].scene_dict
        self.scene._LiveScene__update_scene("", append=False)
    
    def redo_state(self):
        if not self.states_to_redo:
            self.print_gui("There's nothing to redo.")
            return
        self.states.append(self.states_to_redo.pop(0))
        self.scene.__dict__ = self.states[-1].scene_dict
        self.scene._LiveScene__update_scene("", append=False)

    def save_controls(self):
        while not hasattr(self.scene, f"_LiveScene__file_name"):
            time.sleep(0)
        file_name = getattr(
            self.scene, f"_LiveScene__file_name")
        if not file_name:
            return
        controls = [control.to_dict() for control in self.controls.values(
        ) if not isinstance(control, InteractiveMobjectsControl)]
        with open(file_name + "_controls.pkl", "wb") as f:
            pickle.dump(controls, f)

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
        self.save_to_python_action = self.file_menu.addAction(
            "Save to Python Manim File")
        self.save_to_python_action.setShortcut("Ctrl+S")
        self.save_to_python_action.triggered.connect(self.save_to_python)
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.undo_action = self.edit_menu.addAction("Undo")
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.communicate.undo_state.emit)
        self.redo_action = self.edit_menu.addAction("Redo")
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.communicate.redo_state.emit)
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
        self.interactive_preview_window_checkbox = QCheckBox(
            "Enable Interactive Preview Window")
        self.interactive_preview_window_checkbox.setChecked(False)
        self.interactive_preview_window_checkbox.stateChanged.connect(
            lambda: self.interact(self.interactive_preview_window_checkbox.isChecked()))
        self.layout().addWidget(self.interactive_preview_window_checkbox)

    def interact(self, enable: bool):
        self.communicate.enable_interact.emit(enable)
        if self.controls.get("interactive_mobject_dropdown") is None:
            self.add_custom_control_command("interactive_mobject_dropdown", InteractiveMobjectsControl(
                self.communicate, self))

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
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a slider with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a slider with the name 'mouse'. It's reserved for internal use.")
            return
        slider = SliderControl(
            self.communicate, name, (int(min_), int(max_)), int(step), int(default))
        self.controls_widget.add_controls(slider)
        self.communicate.add_value_tracker.emit(
            name, slider.value_tracker)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, slider.value_tracker) if not hasattr(self, name) else None)
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
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a text box with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a text box with the name 'mouse'. It's reserved for internal use.")
            return
        text_box = TextControl(self.communicate, name)
        self.controls_widget.add_controls(text_box)
        self.communicate.add_value_tracker.emit(
            name, text_box.value_tracker)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, text_box.value_tracker) if not hasattr(self, name) else None)
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
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a line box with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a line box with the name 'mouse'. It's reserved for internal use.")
            return
        line_box = LineControl(self.communicate, name)
        self.controls_widget.add_controls(line_box)
        self.communicate.add_value_tracker.emit(
            name, line_box.value_tracker)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, line_box.value_tracker) if not hasattr(self, name) else None)
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
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a color picker with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a color picker with the name 'mouse'. It's reserved for internal use.")
            return
        color_picker = ColorControl(self.communicate, name)
        self.controls_widget.add_controls(color_picker)
        self.communicate.add_value_tracker.emit(
            name, color_picker.value_tracker)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, color_picker.value_tracker) if not hasattr(self, name) else None)
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
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a dropdown with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a dropdown with the name 'mouse'. It's reserved for internal use.")
            return
        dropdown = DropdownControl(self.communicate, name, options)
        self.controls_widget.add_controls(dropdown)
        self.communicate.add_value_tracker.emit(
            name, dropdown.value_tracker)
        self.communicate.add_value_tracker.emit(
            name + "_items", dropdown.list_value_tracker)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, dropdown.value_tracker) if not hasattr(self, name) else None)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name + "_items", dropdown.list_value_tracker) if not hasattr(self, name + "_items") else None)
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
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a checkbox with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a checkbox with the name 'mouse'. It's reserved for internal use.")
            return
        checkbox = CheckboxControl(self.communicate, name, default)
        self.controls_widget.add_controls(checkbox)
        self.communicate.add_value_tracker.emit(
            name, checkbox.value_tracker)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, checkbox.value_tracker) if not hasattr(self, name) else None)
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
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a spin box with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a spin box with the name 'mouse'. It's reserved for internal use.")
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
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, spin_box.value_tracker) if not hasattr(self, name) else None)
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
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a file selector with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a file selector with the name 'mouse'. It's reserved for internal use.")
            return
        file_selector = FileControl(self.communicate, name)
        self.controls_widget.add_controls(file_selector)
        self.communicate.add_value_tracker.emit(
            name, file_selector.value_tracker)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, file_selector.value_tracker) if not hasattr(self, name) else None)
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
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a position control with the name 'mouse'. It's reserved for internal use.")
            return
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a position control with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        position_control = PositionControl(
            self.communicate, name, np.array([float(x), float(y), float(z)]))
        self.controls_widget.add_controls(position_control)
        self.communicate.add_value_tracker.emit(
            name, position_control.value_tracker)
        self.communicate.undo_state.connect(lambda: self.communicate.add_value_tracker.emit(
            name, position_control.value_tracker) if not hasattr(self, name) else None)
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
        set_shortcut_line = QLineEdit()
        set_shortcut_line.setPlaceholderText("Set shortcut")
        dialog.layout().addWidget(set_shortcut_line)
        ok_button = QPushButton("OK")
        dialog.layout().addWidget(ok_button)
        ok_button.clicked.connect(
            lambda: self.add_button_command(name_edit.text(), callback_edit.toPlainText(), set_shortcut_line.text()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    def add_button_command(self, name: str, callback: str, shortcut: str = ""):
        if name == "":
            self.communicate.print_gui.emit(
                "Please enter a name for the button.")
            return
        if name in self.controls:
            self.communicate.print_gui.emit(
                "A control with the same name already exists.")
            return
        if name == "interactive_mobject_dropdown":
            self.communicate.print_gui.emit(
                "Cannot add a button with the name 'interactive_mobject_dropdown'. It's reserved for internal use.")
            return
        if name == "mouse":
            self.communicate.print_gui.emit(
                "Cannot add a button with the name 'mouse'. It's reserved for internal use.")
            return
        button = Button(self.communicate, name, callback)
        if shortcut:
            button.setShortcut(shortcut)
        self.controls_widget.add_controls(button)
        self.controls[name] = button
        return button

    def add_custom_control_command(self, name: str, control: QWidget):
        self.controls_widget.add_controls(control)
        self.controls[name] = control
        return control
