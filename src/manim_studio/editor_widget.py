from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QFileDialog, \
    QMenuBar, QMessageBox, QDialog, QLineEdit, QLabel, QCheckBox, QGridLayout, QScrollArea
from PyQt6.QtGui import QAction, QIntValidator, QColor
from PyQt6.QtCore import pyqtSlot, Qt
import numpy as np
from pathlib import Path
import pickle

from .communicate import Communicate
from .live_scene import LiveScene
from .slider import Slider
from .color_widget import ColorWidget
from .dropdown_widget import DropdownWidget
from .line_editor_widget import LineEditorWidget
from .text_editor_widget import TextEditorWidget
from .checkbox_widget import CheckboxWidget
from .control_dialog import ControlDialog


class EditorWidget(QWidget):
    def __init__(self, communicate: Communicate, scene: LiveScene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.communicate = communicate
        self.setWindowTitle("Manim Studio - Editor")
        self.scene = scene
        self.controls = dict()

        self.code_cell_edit = QTextEdit()
        self.code_cell_edit.setPlaceholderText("Enter your code here")
        self.code_cell_edit.setGeometry(0, 0, 1920, 250)

        self.send_button = QPushButton("Send code")
        self.send_button.setGeometry(0, 0, 100, 50)
        self.send_button.clicked.connect(self.send_code)
        self.end_button = QPushButton("End scene without saving")
        self.end_button.setGeometry(0, 0, 100, 50)
        self.end_button.clicked.connect(self.end_scene)
        self.end_and_save_button = QPushButton("End scene and save")
        self.end_and_save_button.setGeometry(0, 0, 100, 50)
        self.end_and_save_button.clicked.connect(self.end_scene_saving)
        self.save_snip_button = QPushButton("Save snippet")
        self.save_snip_button.setGeometry(0, 0, 100, 50)
        self.save_snip_button.clicked.connect(self.save_snippet)
        self.save_snip_and_run_button = QPushButton("Save snippet and run")
        self.save_snip_and_run_button.setGeometry(0, 0, 100, 50)
        self.save_snip_and_run_button.clicked.connect(
            self.save_snippet_and_run)
        self.communicate.save_snippet.connect(self.save_snippet_command)
        self.next_slide_button = QPushButton("Next slide")
        self.next_slide_button.setGeometry(0, 0, 100, 50)
        self.communicate.next_slide.connect(self.next_slide)
        self.next_slide_button.clicked.connect(
            self.communicate.next_slide.emit)

        self.menu_bar = QMenuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.open_snip_action = QAction("Open snippet", self)
        self.open_snip_action.triggered.connect(self.open_snippet)
        self.file_menu.addAction(self.open_snip_action)
        self.open_snip_and_run_action = QAction(
            "Open snippet and run", self)
        self.open_snip_and_run_action.triggered.connect(
            self.open_snippet_and_run)
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.add_slider_action = QAction("Add slider", self)
        self.add_slider_action.triggered.connect(
            self.add_slider)
        self.edit_menu.addAction(self.add_slider_action)
        self.add_color_widget_action = QAction("Add color widget", self)
        self.add_color_widget_action.triggered.connect(
            self.add_color_widget)
        self.edit_menu.addAction(self.add_color_widget_action)
        self.add_dropdown_action = QAction("Add dropdown", self)
        self.add_dropdown_action.triggered.connect(
            self.add_dropdown)
        self.edit_menu.addAction(self.add_dropdown_action)
        self.add_line_editor_widget_action = QAction(
            "Add line editor widget", self)
        self.add_line_editor_widget_action.triggered.connect(
            self.add_line_editor_widget)
        self.edit_menu.addAction(self.add_line_editor_widget_action)
        self.add_text_editor_widget_action = QAction(
            "Add text editor widget", self)
        self.add_text_editor_widget_action.triggered.connect(
            self.add_text_editor_widget)
        self.edit_menu.addAction(self.add_text_editor_widget_action)
        self.add_checkbox_widget_action = QAction(
            "Add checkbox widget", self)
        self.add_checkbox_widget_action.triggered.connect(
            self.add_checkbox_widget)
        self.edit_menu.addAction(self.add_checkbox_widget_action)

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.menu_bar)
        self.layout_.addWidget(self.code_cell_edit)
        self.layout_.addWidget(self.send_button)
        self.layout_.addWidget(self.end_button)
        self.layout_.addWidget(self.end_and_save_button)
        self.layout_.addWidget(self.save_snip_button)
        self.layout_.addWidget(self.save_snip_and_run_button)
        self.layout_.addWidget(self.next_slide_button)
        self.controls_widget = QWidget()
        self.controls_scroll = QScrollArea()
        self.controls_scroll.setWidget(self.controls_widget)
        self.controls_scroll.setWidgetResizable(True)
        self.no_controls = QLabel(text="No controls defined")
        self.controls_scroll.setWindowTitle("Manim Studio - Controls")
        self.controls_layout = QGridLayout()
        self.controls_layout.addWidget(self.no_controls)
        self.controls_widget.setLayout(self.controls_layout)
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
        self.setLayout(self.layout_)

    def show(self):
        super().show()
        self.controls_scroll.show()

    def add_text_editor_widget(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add text editor widget")
        text_edit = QLineEdit(dialog)
        text_edit.setPlaceholderText("Text editor widget name")
        default_value_edit = QCheckBox(dialog)
        default_value_edit.setText("Is default value True?")
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.close)
        ok_button.clicked.connect(lambda: self.scene.add_text_editor_command(
            text_edit.text(), default_value_edit.text()))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
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

    @pyqtSlot(str, str)
    def add_text_editor_to_editor(self, name: str, default_value: str):
        label = QLabel(text=name)
        text_editor_widget = TextEditorWidget(name)
        text_editor_widget.setText(default_value)
        self.controls[name] = text_editor_widget
        setattr(self.scene, name, text_editor_widget.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(text_editor_widget)
        if self.no_controls.isVisible():
            self.no_controls.hide()

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
        ok_button.clicked.connect(lambda: self.scene.add_dropdown_command(
            text_edit.text(), options_edit.text().split(",")))
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        layout.addWidget(options_edit)
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
        setattr(self.scene, name, line_editor_widget.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(line_editor_widget)
        if self.no_controls.isVisible():
            self.no_controls.hide()

    def send_code(self):
        self.communicate.update_scene.emit(self.code_cell_edit.toPlainText())
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
        setattr(self.scene, name, color_widget.color_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(color_widget)
        if self.no_controls.isVisible():
            self.no_controls.hide()

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
        setattr(self.scene, name, slider.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(slider)
        if self.no_controls.isVisible():
            self.no_controls.hide()

    @pyqtSlot(str, list)
    def add_dropdown_to_editor(self, name: str, options: list[str]):
        label = QLabel(text=name)
        dropdown = DropdownWidget()
        dropdown.addItems(options)
        self.controls[name] = dropdown
        setattr(self.scene, name, dropdown.value_tracker)
        self.controls_layout.addWidget(label)
        self.controls_layout.addWidget(dropdown)
        if self.no_controls.isVisible():
            self.no_controls.hide()

    def save_snippet(self):
        self.communicate.save_snippet.emit(self.code_cell_edit.toPlainText())

    def save_snippet_command(self, code: str):
        controls_dialog = ControlDialog(self.controls)
        controls_dialog.exec()
        add_controls = controls_dialog.add_controls
        if add_controls is True:
            controls_toggle = controls_dialog.controls_toggle
            controls_toggle = {k: v for k,
                               v in controls_toggle.items() if v is True}
        file_ = QFileDialog.getSaveFileName(
            self, "Save snippet", ".", "Manim Studio Snippet (*.mss)")
        if file_[0]:
            with open(file_[0], "w") as f:
                f.write(code)
            if add_controls is True:
                controls = {k: v for k, v in self.controls.items()
                            if k in controls_toggle.keys()}

                def get_tup(v):
                    if isinstance(v, Slider):
                        return ("Slider", v.value(), v.minimum(), v.maximum(), v.singleStep())
                    elif isinstance(v, ColorWidget):
                        return ("ColorWidget", v.currentColor().getRgb())
                    elif isinstance(v, DropdownWidget):
                        return ("DropdownWidget", [v.itemText(i) for i in range(v.count())])
                    elif isinstance(v, LineEditorWidget):
                        return ("LineEditorWidget", v.text())
                    elif isinstance(v, TextEditorWidget):
                        return ("TextEditorWidget", v.toPlainText())
                    elif isinstance(v, CheckboxWidget):
                        return ("CheckboxWidget", v.isChecked())

                controls = {k: get_tup(v) for k, v in controls.items()}
                with open(f"{file_[0]}.controls", "wb") as f:
                    pickle.dump(controls, f)
            else:
                if Path(f"{file_[0]}.controls").exists():
                    Path(f"{file_[0]}.controls").unlink()

    def end_scene_saving(self):
        codes = "\n".join(self.scene.codes)
        self.communicate.save_snippet.emit(codes)
        self.end_scene()

    def save_snippet_and_run(self):
        self.save_snippet()
        self.send_code()

    def open_snippet(self):
        file_ = QFileDialog.getOpenFileName(
            self, "Open snippet", ".", "Manim Studio Snippet (*.mss)")
        if file_[0]:
            with open(file_[0], "r") as f:
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
                            name, control[1])
                    elif control[0] == "LineEditorWidget":
                        self.add_line_editor_widget_to_editor(
                            name, control[1])
                    elif control[0] == "TextEditorWidget":
                        self.add_text_editor_to_editor(
                            name, control[1])
                    elif control[0] == "CheckboxWidget":
                        self.add_checkbox_to_editor(
                            name, control[1])

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
