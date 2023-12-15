from __future__ import annotations
from typing import Callable
from types import ModuleType
from manim import *
from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from .communicate import Communicate
from .save_mobject import save_mobject
from .load_mobject import load_mobject
from manim_studio.value_trackers.boolean_value_tracker import BooleanValueTracker
from manim_studio.value_trackers.string_value_tracker import StringValueTracker
from manim_studio.value_trackers.int_value_tracker import IntValueTracker
from manim_studio.value_trackers.float_value_tracker import FloatValueTracker
from manim_studio.value_trackers.color_value_tracker import ColorValueTracker
from manim_studio.value_trackers.list_value_tracker import ListValueTracker
from manim_studio.value_trackers.dot_tracker import DotTracker
import time


class LiveScene(Scene):
    slideshow = None
    start_inmediately = False

    def __init__(
        self,
        communicate: Communicate,
        mro_without_live_scene: list[type[Scene]],
        module: ModuleType | None = None,
        consider_manim_studio_time: bool = False,
        secrets: dict = {},
        **kwargs
    ):
        self.__current_slide_states = 0
        self.__communicate = communicate
        super().__init__(**kwargs)
        self.__codes = []
        globals()["self"] = self
        self.__current_globals = globals().copy()
        self.__value_trackers_code = ""
        self.__finished = False
        self.__error = False
        self.__current_queue = []
        self.__slide_number = 0
        self.__consider_manim_studio_time = consider_manim_studio_time
        self.__mro_without_live_scene = list(
            map(lambda x: x.__name__, mro_without_live_scene))
        self.__value_trackers = {}
        globals().update(module.__dict__)
        globals()["self"] = self
        del globals()["console"]
        del globals()["error_console"]
        del globals()["logger"]
        self.__communicate.update_scene.connect(self.__update_scene)
        self.__communicate.save_to_python.connect(self.__write_to_python_file)
        self.__communicate.add_value_tracker.connect(self.__add_value_tracker)
        self.__communicate.save_mobject.connect(self.__save_mobject)
        self.__communicate.load_mobject.connect(self.__load_mobject)
        self.__secrets = secrets
        for name, value in self.__secrets.items():
            self.__codes.append(f"setattr(self, {name.__repr__()}, {value.__repr__()})")
    
    def add_slider(self, name: str, min_value: int, max_value: int, step: int, value: int):
        self.__communicate.add_slider.emit(name, min_value, max_value, step, value)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
    
    def add_text_box(self, name: str):
        self.__communicate.add_text_box.emit(name)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
    
    def add_line_box(self, name: str):
        self.__communicate.add_line_box.emit(name)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
    
    def add_color_picker(self, name: str):
        self.__communicate.add_color_picker.emit(name)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
    
    def add_dropdown(self, name: str, options: list):
        self.__communicate.add_dropdown.emit(name, options)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
            
    
    def add_checkbox(self, name: str, value: bool):
        self.__communicate.add_checkbox.emit(name, value)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
            
    
    def add_spin_box(self, name: str, min_value: float, max_value: float, value: float):
        self.__communicate.add_spin_box.emit(name, min_value, max_value, value)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
            
    
    def add_file_selector(self, name: str):
        self.__communicate.add_file_selector.emit(name)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
            
    
    def add_position_control(self, name: str, x: float, y: float, z: float):
        self.__communicate.add_position_control.emit(name, x, y, z)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
            
    
    def add_button(self, name: str, command: str, shortcut: str):
        self.__communicate.add_button.emit(name, command, shortcut)
        while not name in self.__value_trackers and self.__error is False:
            time.sleep(0)
        if self.__error:
            self.__error = False
            

    def wait(self, duration: float = 1.0, stop_condition: Callable[[], bool] | None = None, frozen_frame: bool | None = False):
        super().wait(duration, stop_condition, frozen_frame)

    def __add_value_tracker(self, name: str, value_tracker: ValueTracker) -> None:
        """
        Add a value tracker.

        Parameters
        ----------
        name
            The name of the value tracker.
        value_tracker
            The value tracker to be added.
        """
        self.__value_trackers[name] = value_tracker
        setattr(self, name, value_tracker)
        self.__value_trackers_code += f"        setattr(self, {name.__repr__()}, {value_tracker.__repr__()})\n"

    def __get_code(self) -> str:
        """
        Get the code of the state.

        Parameters
        ----------
        state
            The name of the state.
        """
        CODE = """from manim import *
from manim_studio.value_trackers.boolean_value_tracker import BooleanValueTracker
from manim_studio.value_trackers.string_value_tracker import StringValueTracker
from manim_studio.value_trackers.int_value_tracker import IntValueTracker
from manim_studio.value_trackers.float_value_tracker import FloatValueTracker
from manim_studio.value_trackers.color_value_tracker import ColorValueTracker
from manim_studio.value_trackers.dot_tracker import DotTracker
from manim_studio.value_trackers.list_value_tracker import ListValueTracker
from manim_studio.load_mobject import load_mobject
from typing import Callable
import time


class Result({}):
    slideshow = None
    start_inmediately = False

    def construct(self):
{}
        {}
    
    def print_gui(self, text: str) -> None:
        print(text)
"""
        if not self.__codes or all(code.strip() == "" for code in self.__codes):
            return CODE.format(",".join(self.__mro_without_live_scene), self.__value_trackers_code, "pass")
        return CODE.format(','.join(self.__mro_without_live_scene), self.__value_trackers_code, "\n        ".join(line for lines in self.__codes for line in lines.split("\n")))

    def construct(self):
        self.wait(1 / self.camera.frame_rate)
        self.__communicate.save_state.emit()
        if self.slideshow is not None and self.start_inmediately:
            self.__update_scene(self.slideshow[0])
            self.__slide_number += 1
        while not self.__finished:
            if self.__consider_manim_studio_time:
                self.__current_animation_start_time = self.renderer.time
            while not self.__current_queue:
                self.wait_until(lambda: bool(self.__current_queue))
            if self.__consider_manim_studio_time:
                frames_passed = self.renderer.time - \
                    self.__current_animation_start_time
                frames_passed = round(
                    frames_passed * self.camera.frame_rate)
                if frames_passed > 0:
                    self.__codes.append(
                        f"self.wait({frames_passed} / self.camera.frame_rate)")
            self.__run_current_code()

    def __update_scene(self, code: str, append: bool = True) -> None:
        """
        Update the scene.

        Parameters
        ----------
        code
            The code to update the scene.
        """
        self.__current_queue.append((code, append))

    def __run_current_code(self) -> None:
        """
        Run the current code.
        """
        while self.__current_queue:
            code, append_code = self.__current_queue.pop(0)
            self.__codes.append(code)
            if append_code:
                self.__communicate.save_state.emit()
            try:
                exec(code, self.__current_globals)
            except EndSceneEarlyException:
                self.__finished = True
                self.__current_queue.clear()
            except Exception as e:
                self.__communicate.print_gui.emit(
                    f"{e.__class__.__name__}: {e}")
                self.__current_queue.clear()
                self.__communicate.undo_state.emit(True)
                
            else:
                self.__communicate.update_state.emit()
            if append_code:
                self.__current_slide_states += 1

    def __save_mobject(self) -> None:
        """
        Save the mobject.

        Parameters
        ----------
        mobject
            The mobject to be saved.
        name
            The name of the mobject.
        """
        dialog = QDialog()
        dialog.setWindowTitle("Save Mobject")
        dialog.setLayout(QVBoxLayout(dialog))
        dialog.layout().setContentsMargins(0, 0, 0, 0)
        dialog.label = QLabel("Enter the mobject name (without self.):")
        dialog.layout().addWidget(dialog.label)
        dialog.line_edit = QLineEdit()
        dialog.layout().addWidget(dialog.line_edit)
        dialog.button = QPushButton("Save")
        dialog.button.clicked.connect(dialog.accept)
        dialog.layout().addWidget(dialog.button)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Rejected or dialog.line_edit.text() == "":
            self.__communicate.print_gui.emit(
                "No mobject name is given. The mobject was not saved."
            )
            return
        name = dialog.line_edit.text()
        file_name, _ = QFileDialog.getSaveFileName(
            None, "Save Mobject", "", "Pickle File (*.pkl)"
        )
        if file_name:
            save_mobject(getattr(self, name), file_name, globals())
            self.__communicate.print_gui.emit(
                f"The mobject {name} was saved successfully."
            )
        else:
            self.__communicate.print_gui.emit(
                "No file name is given. The mobject was not saved."
            )

    def __load_mobject(self) -> None:
        """
        Load the mobject.

        Parameters
        ----------
        name
            The name of the mobject.
        """
        dialog = QDialog()
        dialog.setWindowTitle("Load Mobject")
        dialog.setLayout(QVBoxLayout(dialog))
        dialog.layout().setContentsMargins(0, 0, 0, 0)
        dialog.label = QLabel("Enter the mobject name (without self.):")
        dialog.layout().addWidget(dialog.label)
        dialog.line_edit = QLineEdit()
        dialog.layout().addWidget(dialog.line_edit)
        dialog.button = QPushButton("Load")
        dialog.button.clicked.connect(dialog.accept)
        dialog.layout().addWidget(dialog.button)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Rejected or dialog.line_edit.text() == "":
            self.__communicate.print_gui.emit(
                "No mobject name is given. The mobject was not loaded."
            )
            return
        name = dialog.line_edit.text()
        file_name, _ = QFileDialog.getOpenFileName(
            None, "Load Mobject", "", "Pickle File (*.pkl)"
        )
        if file_name:
            self.__communicate.update_scene.emit(
                f"setattr(self, {name.__repr__()}, load_mobject({file_name.__repr__()}))")
            self.__communicate.print_gui.emit(
                f"The mobject {name} was loaded successfully. Add it to the scene by running:\nself.add(getattr(self, {name.__repr__()}))")  # noqa
        else:
            self.__communicate.print_gui.emit(
                "No file name is given. The mobject was not loaded."
            )

    def print_gui(self, text: str) -> None:
        """
        Print the text in the GUI.

        Parameters
        ----------
        text
            The text to be printed.
        """
        self.__communicate.print_gui.emit(text.__repr__())

    def __write_to_python_file(self) -> None:
        """
        Write the code to a python file.

        Parameters
        ----------
        state
            The name of the state.
        """
        file_name, _ = QFileDialog.getSaveFileName(
            None, "Save Python File", "", "Python File (*.py)"
        )
        if file_name:
            with open(file_name, "w") as f:
                f.write(self.__get_code())
            self.__communicate.show_in_status_bar.emit(
                f"The code was saved successfully."
            )
            self.__communicate.print_gui.emit(
                f"The code was saved successfully."
            )
        else:
            self.__communicate.show_in_status_bar.emit(
                "No file name is given. The code was not saved."
            )

    def update_to_time(self, t):
        super().update_to_time(t)
        self.__communicate.update_image.emit(self.renderer.get_frame())
