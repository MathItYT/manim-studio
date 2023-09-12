from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QFileDialog, \
    QMenuBar, QMessageBox, QDialog, QLineEdit, QLabel
from PyQt6.QtGui import QAction, QIntValidator
from PyQt6.QtCore import pyqtSlot

from .communicate import Communicate
from .live_scene import LiveScene


class EditorWidget(QWidget):
    def __init__(self, communicate: Communicate, scene: LiveScene, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.communicate = communicate
        self.setWindowTitle("Manim Studio - Editor")
        self.setGeometry(0, 0, 1920, 500)
        self.scene = scene

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter your code here")
        self.text_edit.setGeometry(0, 0, 1920, 250)

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

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.menu_bar)
        self.layout_.addWidget(self.text_edit)
        self.layout_.addWidget(self.send_button)
        self.layout_.addWidget(self.end_button)
        self.layout_.addWidget(self.end_and_save_button)
        self.layout_.addWidget(self.save_snip_button)
        self.layout_.addWidget(self.save_snip_and_run_button)
        self.layout_.addWidget(self.next_slide_button)
        self.communicate.add_slider_to_editor.connect(
            self.add_slider_to_editor)
        self.setLayout(self.layout_)

    def send_code(self):
        self.communicate.update_scene.emit(self.text_edit.toPlainText())
        self.text_edit.clear()

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

    @pyqtSlot(str)
    def add_slider_to_editor(self, name: str):
        label = QLabel(text=name)
        self.layout_.addWidget(label)
        self.layout_.addWidget(self.scene.sliders[name])
        self.setGeometry(0, 0, 1920, self.height() + 50)

    def save_snippet(self):
        self.communicate.save_snippet.emit(self.text_edit.toPlainText())

    def save_snippet_command(self, code: str):
        file_ = QFileDialog.getSaveFileName(
            self, "Save snippet", ".", "Manim Studio Snippet (*.mss)")
        if file_[0]:
            with open(file_[0], "w") as f:
                f.write(code)

    def end_scene_saving(self):
        codes = "\n".join(self.scene.codes)
        file_ = QFileDialog.getSaveFileName(
            self, "Save snippet", ".", "Manim Studio Snippet (*.mss)")
        if file_[0]:
            with open(file_[0], "w") as f:
                f.write(codes)
        self.end_scene()

    def save_snippet_and_run(self):
        self.save_snippet()
        self.send_code()

    def open_snippet(self):
        file_ = QFileDialog.getOpenFileName(
            self, "Open snippet", ".", "Manim Studio Snippet (*.mss)")
        if file_[0]:
            with open(file_[0], "r") as f:
                self.text_edit.setText(
                    f"{self.text_edit.toPlainText()}\n{f.read()}")

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
