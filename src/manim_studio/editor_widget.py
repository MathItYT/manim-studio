from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QFileDialog, QMenuBar
from PyQt6.QtGui import QAction

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

        self.menu_bar = QMenuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.open_snip_action = QAction("Open snippet", self)
        self.open_snip_action.triggered.connect(self.open_snippet)
        self.file_menu.addAction(self.open_snip_action)

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.menu_bar)
        self.layout_.addWidget(self.text_edit)
        self.layout_.addWidget(self.send_button)
        self.layout_.addWidget(self.end_button)
        self.layout_.addWidget(self.end_and_save_button)
        self.layout_.addWidget(self.save_snip_button)
        self.layout_.addWidget(self.save_snip_and_run_button)
        self.setLayout(self.layout_)

    def send_code(self):
        self.communicate.update_scene.emit(self.text_edit.toPlainText())
        self.text_edit.clear()

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

    def end_scene(self):
        self.communicate.end_scene.emit()
