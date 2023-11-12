from manim import *
from PyQt6.QtCore import QObject, pyqtSlot, Qt
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog
from .communicate import Communicate
from PIL import Image
import dill as pickle
import time
import ctypes

from .load_mobject import load_mobject


class CairoLiveRenderer(QObject, CairoRenderer):
    def __init__(self, communicate: Communicate, camera_class=None, *args, **kwargs):
        QObject.__init__(self)
        CairoRenderer.__init__(
            self, camera_class=camera_class, *args, **kwargs)
        self.communicate = communicate

    def render(self, scene, time, moving_mobjects):
        super().render(scene, time, moving_mobjects)
        self.communicate.update_image.emit(self.get_frame())


class LiveScene(QObject, Scene):
    def __init__(self, communicate: Communicate, namespace=None, *args, **kwargs):
        config.disable_caching = True
        self.communicate = communicate
        super().__init__(*args, **kwargs)
        self.renderer = CairoLiveRenderer(
            communicate, camera_class=self.camera_class)
        self.renderer.init_scene(self)
        self.communicate.update_scene.connect(self.update_scene)
        self.communicate.end_scene.connect(self.end_scene)
        self.communicate.alert.connect(self.alert)
        self.communicate.save_mobject.connect(self.save_mobject)
        self.communicate.load_mobject.connect(self.load_mobject)
        self.communicate.pause_scene.connect(self.pause_scene)
        self.communicate.resume_scene.connect(self.resume_scene)
        self.communicate.screenshot.connect(self.screenshot)
        self.current_code = None
        self.namespace = namespace.__dict__ if namespace is not None else {}
        self.freeze = False
        self.paused = False
        self.playing = False
        self.append_line = True
        self.scope = globals()
        self.scope.update(self.namespace)
        self.scope["self"] = self
        if isinstance(self, MovingCameraScene):
            self.add(self.camera.frame)
        self.states = {}

    def screenshot(self, name: str):
        arr = self.renderer.get_frame()
        Image.fromarray(arr).save(name)

    def save_state(self, name: str | None = None):
        if name is None or name.strip() == "":
            name = "Untitled"
        name = str(name).strip()
        if name in self.states.keys():
            self.print_gui(f"State '{name}' already exists.")
            return False
        self.states[name] = [[m.__dict__.copy() for m in self.mobjects], [
            id(m) for m in self.mobjects]]
        self.print_gui(f"State '{name}' saved.")
        return True

    def restore_state(self, name: str):
        name = str(name).strip()
        copy_dicts, ids = self.states.get(name, (None, None))
        if copy_dicts is None:
            self.print_gui(f"State '{name}' does not exist.")
            return False
        mobjects = [ctypes.cast(i, ctypes.py_object).value for i in ids]
        for mobject, copy_dict in zip(mobjects, copy_dicts):
            mobject.__dict__ = copy_dict
        self.mobjects = mobjects
        self.print_gui(f"State '{name}' restored.")
        return True

    def print_gui(self, text: str):
        self.communicate.print_gui.emit(str(text))

    def pause_scene(self):
        self.paused = True

    def resume_scene(self):
        self.paused = False

    def set_control_value(self, name: str, value: str):
        self.communicate.set_control_value.emit(name, value)

    def construct(self):
        while True:
            while self.no_instruction() and not self.paused:
                self.wait_until(
                    lambda: not self.no_instruction() or self.paused, 1)
            if self.paused:
                while self.paused:
                    time.sleep(0)
            if not self.no_instruction():
                self.run_instruction()

    def add_checkbox_command(self, name: str, default_value: bool):
        caller_function = inspect.stack()[1].function
        self.communicate.add_checkbox_to_editor.emit(
            name, default_value)

    def add_text_editor_command(self, name: str, default_value: str):
        self.communicate.add_text_editor_to_editor.emit(
            name, default_value)

    def add_line_edit_command(self, name: str, default_value: str):
        self.communicate.add_line_edit_to_editor.emit(
            name, default_value)

    def add_dropdown_command(self, name: str, options: list[str], default_value: str):
        self.communicate.add_dropdown_to_editor.emit(
            name, options, default_value)

    def add_color_widget_command(self, name: str, default_value: np.ndarray):
        self.communicate.add_color_widget_to_editor.emit(
            name, default_value)

    def add_slider_command(self, name: str, default_value: str, min_value: str, max_value: str, step_value: str):
        self.communicate.add_slider_to_editor.emit(
            name, default_value, min_value, max_value, step_value)

    def add_button_command(self, name: str, callback: str):
        self.communicate.add_button_to_editor.emit(
            name, callback)

    def wait(self, *args, frozen_frame=False, **kwargs):
        super().wait(*args, frozen_frame=frozen_frame, **kwargs)

    def run_instruction(self):
        try:
            current_code = self.current_code
            self.current_code = None
            self.scope["self"] = self
            exec(current_code, self.scope)
        except EndSceneEarlyException:
            raise EndSceneEarlyException()
        except Exception as e:
            logger.info(
                f"Exception occured in live scene ({e.__class__.__name__}: {e})")
            self.communicate.alert.emit(e)

    def add_position_control_command(self, name: str, default_value: np.ndarray):
        self.communicate.add_position_control_to_editor.emit(
            name, default_value)

    @pyqtSlot(str)
    def update_scene(self, code: str):
        if self.freeze and code != "raise EndSceneEarlyException()":
            alert = QMessageBox(
                text="You cannot update the scene while it is paused.")
            alert.setWindowTitle("Scene paused")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            alert.exec()
            return
        self.current_code = code

    @pyqtSlot()
    def end_scene(self):
        self.current_code = "raise EndSceneEarlyException()"
        alert = QMessageBox(
            text="Your scene has ended. See the terminal for more information.")
        alert.setWindowTitle("Scene ended")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        alert.exec()

    @pyqtSlot(Exception)
    def alert(self, e: Exception):
        alert = QMessageBox(
            text="An error occured while processing your code.")
        alert.setWindowTitle("Error")
        alert.setIcon(QMessageBox.Icon.Warning)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.setInformativeText(f"{e.__class__.__name__}: {e}")
        alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        alert.exec()

    def pause_slide(self):
        self.freeze = True
        while self.freeze and self.no_instruction():
            self.wait_until(
                lambda: not self.freeze or not self.no_instruction(), 1)
        if not self.no_instruction():
            self.run_instruction()
        self.freeze = False

    def no_instruction(self):
        return self.current_code is None

    def save_mobject(self):
        dialog = QDialog()
        dialog.setWindowTitle("Save mobject")
        dialog.layout_ = QVBoxLayout()
        dialog.name_edit = QLineEdit()
        dialog.name_edit.setPlaceholderText("Enter the name of the mobject")
        dialog.info_label = QLabel(
            text="The name of the mobject must be a valid attribute of the scene.\n"
            "For example, if you want to save the mobject 'self.circle',\n"
            "you must enter 'circle' in the text box below.")
        dialog.layout_.addWidget(dialog.name_edit)
        dialog.layout_.addWidget(dialog.info_label)
        dialog.ok_button = QPushButton("OK")
        dialog.ok_button.clicked.connect(dialog.accept)
        dialog.layout_.addWidget(dialog.ok_button)
        dialog.setLayout(dialog.layout_)
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        dialog.exec()

        name = dialog.name_edit.text()
        if name == "":
            alert = QMessageBox(
                text="You must enter a name for the mobject.")
            alert.setWindowTitle("No name entered")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            alert.exec()
            return
        mobject_to_save = getattr(self, name, None)
        if mobject_to_save is None:
            alert = QMessageBox(
                text="The name you entered is not a valid attribute of the scene.")
            alert.setWindowTitle("Invalid name")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            alert.exec()
            return
        file_name = QFileDialog.getSaveFileName(
            caption="Save mobject",
            filter="Pickle file (*.pkl)"
        )
        if file_name[0]:
            with open(file_name[0], "wb") as f:
                pickle.dump(mobject_to_save, f)
        else:
            alert = QMessageBox(
                text="You must enter a file name.")
            alert.setWindowTitle("No file name entered")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            alert.exec()
            return
        alert = QMessageBox(
            text="The mobject has been saved.")
        alert.setWindowTitle("Mobject saved")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        alert.exec()

    def load_mobject(self):
        file_name = QFileDialog.getOpenFileName(
            caption="Load mobject",
            filter="Pickle file (*.pkl)"
        )
        if not file_name[0]:
            alert = QMessageBox(
                text="You must enter a file name.")
            alert.setWindowTitle("No file name entered")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            alert.exec()
            return
        dialog = QDialog()
        dialog.setWindowTitle("Load mobject")
        dialog.layout_ = QVBoxLayout()
        dialog.name_edit = QLineEdit()
        dialog.name_edit.setPlaceholderText("Enter the name of the mobject")
        dialog.info_label = QLabel(
            text="The name of the mobject will be an attribute of the scene.\n"
            "For example, if you want to load the mobject as 'self.circle',\n"
            "you must enter 'circle' in the text box below.")
        dialog.layout_.addWidget(dialog.name_edit)
        dialog.layout_.addWidget(dialog.info_label)
        dialog.ok_button = QPushButton("OK")
        dialog.ok_button.clicked.connect(dialog.accept)
        dialog.layout_.addWidget(dialog.ok_button)
        dialog.setLayout(dialog.layout_)
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        dialog.exec()
        if dialog.name_edit.text() == "":
            alert = QMessageBox(
                text="You must enter a name for the mobject.")
            alert.setWindowTitle("No name entered")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            alert.exec()
            return
        code = f"self.{dialog.name_edit.text()} = load_mobject('{file_name[0]}')"
        self.communicate.update_scene.emit(code)
        alert = QMessageBox(
            text="The mobject has been loaded.")
        alert.setWindowTitle("Mobject loaded")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        alert.exec()
