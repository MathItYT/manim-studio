from manim import *
from PyQt6.QtCore import QObject, pyqtSlot, Qt
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog
from .communicate import Communicate
from PIL import Image
import time
import ctypes
from manim_studio.saving_and_loading_mobjects import save_mobject, load_mobject
from manim_studio.value_trackers.boolean_value_tracker import BooleanValueTracker
from manim_studio.value_trackers.color_value_tracker import ColorValueTracker
from manim_studio.value_trackers.int_value_tracker import IntValueTracker
from manim_studio.value_trackers.string_value_tracker import StringValueTracker


class CalledFromEditorException(Exception):
    pass


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
        self.value_trackers = {}
        self.codes = {}
        self.append_code = True
        self.namespace = namespace.__dict__ if namespace is not None else {}
        self.freeze = False
        self.paused = False
        self.called_from_editor = True
        self.python_file_to_write = None
        self.scope = globals()
        self.scope.update(self.namespace)
        self.scope["self"] = self
        if isinstance(self, MovingCameraScene):
            self.add(self.camera.frame)
        self.states = {}
        self.save_state("first")

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
        if name == "temp" and not self.called_from_editor:
            self.print_gui(
                "Cannot save to 'temp'. It's reserved for internal use.")
            return False
        self.states[name] = [[m.__dict__.copy() for m in self.mobjects], [
            id(m) for m in self.mobjects]]
        if name != "temp":
            self.current_state = name
            self.codes[name] = []
        if not self.called_from_editor:
            self.print_gui(f"State '{name}' saved.")
        return True

    def remove_state(self, name: str):
        name = str(name).strip()
        if name == "":
            self.print_gui("You must enter a name.")
            return False
        if name not in self.states.keys():
            self.print_gui(f"State '{name}' does not exist.")
            return False
        del self.states[name]
        if name == "temp" and not self.called_from_editor:
            self.print_gui(
                "Cannot remove 'temp'. It's reserved for internal use.")
            return False
        if name == "first":
            self.print_gui(
                "Cannot remove 'first'. It's reserved for internal use.")
            return False
        if not self.called_from_editor:
            self.print_gui(f"State '{name}' removed.")
        if name != "temp":
            del self.codes[name]
        return True

    def restore_state(self, name: str):
        name = str(name).strip()
        if name == "":
            self.print_gui("You must enter a name.")
            return False
        copy_dicts, ids = self.states.get(name, (None, None))
        if copy_dicts is None:
            self.print_gui(f"State '{name}' does not exist.")
            return False
        mobjects = [ctypes.cast(i, ctypes.py_object).value for i in ids]
        for mobject, copy_dict in zip(mobjects, copy_dicts):
            mobject.__dict__ = copy_dict
        self.mobjects = mobjects
        if name != "temp":
            self.current_state = name
        if not self.called_from_editor:
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
        self.called_from_editor = False
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
        if self.called_from_editor:
            raise CalledFromEditorException("Cannot add widgets from editor")
        self.communicate.add_checkbox_to_editor.emit(
            name, default_value)

    def add_text_editor_command(self, name: str, default_value: str):
        if self.called_from_editor:
            raise CalledFromEditorException("Cannot add widgets from editor")
        self.communicate.add_text_editor_to_editor.emit(
            name, default_value)

    def add_line_edit_command(self, name: str, default_value: str):
        if self.called_from_editor:
            raise CalledFromEditorException("Cannot add widgets from editor")
        self.communicate.add_line_edit_to_editor.emit(
            name, default_value)

    def add_dropdown_command(self, name: str, options: list[str], default_value: str):
        if self.called_from_editor:
            raise CalledFromEditorException("Cannot add widgets from editor")
        self.communicate.add_dropdown_to_editor.emit(
            name, options, default_value)

    def add_color_widget_command(self, name: str, default_value: np.ndarray):
        if self.called_from_editor:
            raise CalledFromEditorException("Cannot add widgets from editor")
        self.communicate.add_color_widget_to_editor.emit(
            name, default_value)

    def add_slider_command(self, name: str, default_value: str, min_value: str, max_value: str, step_value: str):
        if self.called_from_editor:
            raise CalledFromEditorException("Cannot add widgets from editor")
        self.communicate.add_slider_to_editor.emit(
            name, default_value, min_value, max_value, step_value)

    def add_button_command(self, name: str, callback: str):
        if self.called_from_editor:
            raise CalledFromEditorException("Cannot add widgets from editor")
        self.communicate.add_button_to_editor.emit(
            name, callback)

    def wait(self, *args, frozen_frame=False, **kwargs):
        super().wait(*args, frozen_frame=frozen_frame, **kwargs)

    def replay_from_state(self, name: str):
        if name == "" and self.python_file_to_write is not None:
            self.print_gui("You must enter a name. Anyways, you can go to 'States' tab "
                           "and click on 'Replay from state' button to export to Python file.")
            return
        self.called_from_editor = True
        self.restore_state(name)
        self.current_code = "\n".join(self.codes[name])
        if self.python_file_to_write is not None:
            CODE = """from manim import *
from manim_studio.value_trackers.boolean_value_tracker import BooleanValueTracker
from manim_studio.value_trackers.color_value_tracker import ColorValueTracker
from manim_studio.value_trackers.int_value_tracker import IntValueTracker
from manim_studio.value_trackers.string_value_tracker import StringValueTracker

            
class Result(%s):
    def construct(self):%s
        %s
    
    def print_gui(self, text: str):
        print(text)""" % (",".join([i.__name__ for i in self.__class__.__bases__ if i.__name__ not in ("LiveScene", "QObject")]),
                          self.get_value_trackers_code(),
                          "\n        ".join([line for code in self.codes[name] for line in code.split("\n") if line.strip() != ""]))
            with open(self.python_file_to_write, "w") as f:
                f.write(CODE)
            self.print_gui("Python file has been exported.")
            self.python_file_to_write = None

    def get_value_trackers_code(self):
        code = ""
        for name, value_tracker in self.value_trackers.items():
            if isinstance(value_tracker, BooleanValueTracker):
                code += f"\n        self.{
                    name} = BooleanValueTracker({value_tracker.get_value()})"
            elif isinstance(value_tracker, ColorValueTracker):
                value = value_tracker.get_value()
                hex_ = value[0]
                alpha = value[1]
                r, g, b = color_to_rgb(hex_)
                code += f"\n        self.{
                    name} = ColorValueTracker(np.array([{r}, {g}, {b}, {alpha}]))"
            elif isinstance(value_tracker, IntValueTracker):
                code += f"\n        self.{
                    name} = IntValueTracker({value_tracker.get_value()})"
            elif isinstance(value_tracker, StringValueTracker):
                code += f"\n        self.{
                    name} = StringValueTracker({value_tracker.get_value()})"
        return code

    def run_instruction(self):
        try:
            self.called_from_editor = True
            self.save_state("temp")
            current_code = self.current_code
            self.current_code = None
            self.scope["self"] = self
            current_scope = self.scope.copy()
            exec(current_code, self.scope)
        except EndSceneEarlyException:
            raise EndSceneEarlyException()
        except Exception as e:
            logger.info(
                f"Exception occured in live scene ({e.__class__.__name__}: {e})")
            self.communicate.alert.emit(e)
            self.restore_state("temp")
            self.scope = current_scope
        else:
            if self.append_code:
                self.codes[self.current_state].append(current_code)
        finally:
            self.remove_state("temp")
            self.called_from_editor = False

    def add_position_control_command(self, name: str, default_value: np.ndarray):
        if self.called_from_editor:
            raise CalledFromEditorException("Cannot add widgets from editor")
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
            alert.exec()
            return
        if self.paused:
            self.resume_scene()
        self.current_code = code

    @pyqtSlot()
    def end_scene(self):
        self.current_code = "raise EndSceneEarlyException()"
        alert = QMessageBox(
            text="Your scene has ended. See the terminal for more information.")
        alert.setWindowTitle("Scene ended")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.exec()

    @pyqtSlot(Exception)
    def alert(self, e: Exception):
        alert = QMessageBox(
            text="An error occured while processing your code.")
        alert.setWindowTitle("Error")
        alert.setIcon(QMessageBox.Icon.Warning)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.setInformativeText(f"{e.__class__.__name__}: {e}")
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
        dialog.exec()

        name = dialog.name_edit.text()
        if name == "":
            alert = QMessageBox(
                text="You must enter a name for the mobject.")
            alert.setWindowTitle("No name entered")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.exec()
            return
        mobject_to_save = getattr(self, name, None)
        if mobject_to_save is None:
            alert = QMessageBox(
                text="The name you entered is not a valid attribute of the scene.")
            alert.setWindowTitle("Invalid name")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.exec()
            return
        file_name = QFileDialog.getSaveFileName(
            caption="Save mobject",
            filter="Pickle (*.pkl)"
        )
        if file_name[0]:
            save_mobject(mobject_to_save, file_name[0], self.scope)
        else:
            alert = QMessageBox(
                text="You must enter a file name.")
            alert.setWindowTitle("No file name entered")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.exec()
            return
        alert = QMessageBox(
            text="The mobject has been saved.")
        alert.setWindowTitle("Mobject saved")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.exec()

    def load_mobject(self):
        file_name = QFileDialog.getOpenFileName(
            caption="Load mobject",
            filter="Pickle (*.pkl)"
        )
        if not file_name[0]:
            alert = QMessageBox(
                text="You must enter a file name.")
            alert.setWindowTitle("No file name entered")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
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
        dialog.exec()
        if dialog.name_edit.text() == "":
            alert = QMessageBox(
                text="You must enter a name for the mobject.")
            alert.setWindowTitle("No name entered")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
            alert.exec()
            return
        code = f"self.{dialog.name_edit.text()} = load_mobject('{
            file_name[0]}')"
        self.communicate.update_scene.emit(code)
        alert = QMessageBox(
            text="The mobject has been loaded.")
        alert.setWindowTitle("Mobject loaded")
        alert.setIcon(QMessageBox.Icon.Information)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.exec()
