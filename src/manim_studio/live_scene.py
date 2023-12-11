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
from manim_studio.control_mobjects.manim_slider import ManimSlider
import time


class LiveScene(Scene):
    def __init__(
        self,
        communicate: Communicate,
        mro_without_live_scene: list[type[Scene]],
        project: str = "",
        module: ModuleType | None = None,
        consider_manim_studio_time: bool = False,
        **kwargs
    ):
        self.__communicate = communicate
        super().__init__(**kwargs)
        self.__states = {}
        self.__codes = {}
        self.__finished = False
        self.__current_queue = []
        self.__starting = True
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
        self.__communicate.save_state.connect(self.__save_state)
        self.__communicate.restore_state.connect(self.__restore_state)
        self.__communicate.remove_state.connect(self.__remove_state)
        self.__communicate.add_value_tracker.connect(self.__add_value_tracker)
        self.__communicate.save_mobject.connect(self.__save_mobject)
        self.__communicate.load_mobject.connect(self.__load_mobject)
        self.__communicate.save_project.connect(self.__save_project)
        self.__communicate.load_project.connect(self.__load_project)
        self.__project = project

    def __load_project(self, project: str) -> None:
        with open(project, "r") as f:
            codes = f.read().split("\n---\n")
        if len(codes) < 3:
            return
        for code in codes[2:]:
            self.__communicate.update_scene.emit(code)

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
        self.__communicate.update_scene.emit(
            f"setattr(self, {name.__repr__()}, {value_tracker.__repr__()})")

    def __save_state(self, name: str) -> None:
        """
        Save the current state of the scene.

        Parameters
        ----------
        name
            The name of the state.
        """
        if name in self.__states:
            raise ValueError(f"The state {name} already exists.")
        if hasattr(self, f"_LiveScene__current_state"):
            dct = self.__dict__.copy()
            dct.pop(f"_LiveScene__states")
            self.__states[self.__current_state] = (
                dct, globals().copy())
        dct = self.__dict__.copy()
        dct.pop(f"_LiveScene__states")
        self.__states[name] = (dct, globals().copy())
        self.__codes[name] = []
        if name != "temp":
            if isinstance(self, MovingCameraScene):
                self.camera.frame.stretch_to_fit_width(config["frame_width"])
                self.camera.frame.stretch_to_fit_height(config["frame_height"])
                self.camera.frame.move_to(ORIGIN)
            self.mobjects = []
            self.__get_into_state(name)
            self.__communicate.show_in_status_bar.emit(
                f"The state {name} was saved successfully."
            )

    def __restore_state(self, name: str) -> None:
        """
        Restore the state of the scene.

        Parameters
        ----------
        name
            The name of the state.
        """
        if name not in self.__states:
            raise ValueError(f"The state {name} does not exist.")
        dct = self.__dict__.copy()
        dct.pop(f"_LiveScene__states")
        self.__states[self.__current_state] = (
            dct, globals().copy())
        for key in globals().copy():
            if key not in self.__states[name][1]:
                del globals()[key]
        globals().update(self.__states[name][1])
        for key in self.__states[name][0].copy():
            if key not in self.__dict__ and key != f"_LiveScene__states":
                del self.__states[name][0][key]
        self.__dict__.update(self.__states[name][0])
        dct = self.__dict__.copy()
        dct.pop(f"_LiveScene__states")
        self.__states[name] = (dct, globals().copy())
        self.__communicate.update_scene.emit("")
        if name != "temp":
            self.__get_into_state(name)
            self.__communicate.show_in_status_bar.emit(
                f"The state {name} was restored successfully.")

    def __remove_state(self, name: str) -> None:
        """
        Remove the state of the scene.

        Parameters
        ----------
        name
            The name of the state.
        """
        if name == "first":
            self.__communicate.show_in_status_bar.emit(
                "Cannot remove the first state.")
            return
        del self.__states[name]
        del self.__codes[name]
        if name != "temp":
            self.__communicate.show_in_status_bar.emit(
                f"The state {name} was removed successfully."
            )

    def __get_into_state(self, name: str) -> None:
        """
        Get into the state of the scene.

        Parameters
        ----------
        name
            The name of the state.
        """
        self.__current_state = name
        self.__communicate.show_in_status_bar.emit(
            f"Current state: {name}")

    def __save_code(self, code: str, state: str) -> None:
        """
        Save the current code.

        Parameters
        ----------
        code
            The current code.
        """
        self.__codes[state].append(code)

    def __save_project(self) -> None:
        """
        Save the current project.

        Parameters
        ----------
        state
            The name of the state.
        """
        file_name, _ = QFileDialog.getSaveFileName(
            None, "Save Project", "", "No Format (*.)"
        )
        if file_name:
            with open(file_name, "w") as f:
                f.write(
                    ",".join([base.__name__ for base in self.__class__.__bases__]))
                f.write("\n---\n" + self.__class__.__name__ + "\n---\n")
                f.write("\n---\n".join(self.__codes[self.__current_state]))
            self.__communicate.show_in_status_bar.emit(
                f"The project was saved successfully."
            )
            self.__communicate.print_gui.emit(
                f"The project was saved successfully."
            )
        self.__file_name = file_name

    def __get_code(self, state: str) -> str:
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
from manim_studio.control_mobjects.manim_slider import ManimSlider
from typing import Callable
import time


class Result({}):
    def construct(self):
        {}
    
    def print_gui(self, text: str) -> None:
        print(text)
"""
        if not self.__codes[state] or all(code.strip() == "" for code in self.__codes[state]):
            return CODE.format(",".join(self.__mro_without_live_scene), "pass")
        return CODE.format(','.join(self.__mro_without_live_scene), "\n        ".join(line for lines in self.__codes[state] for line in lines.split("\n")))

    def construct(self):
        if self.__project:
            self.__communicate.load_project.emit(self.__project)
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
                self.__codes[self.__current_state].append(
                    f"self.wait({frames_passed} / self.camera.frame_rate)")
            self.__run_current_code()

    def __update_scene(self, code: str) -> None:
        """
        Update the scene.

        Parameters
        ----------
        code
            The code to update the scene.
        """
        self.__current_queue.append(code)

    def __run_current_code(self) -> None:
        """
        Run the current code.
        """
        while self.__current_queue:
            self.__save_state("temp")
            code = self.__current_queue.pop(0)
            try:
                exec(code, globals())
            except EndSceneEarlyException:
                self.__finished = True
            except Exception as e:
                self.__communicate.print_gui.emit(
                    f"{e.__class__.__name__}: {e}")
                self.__restore_state("temp")
            else:

                self.__save_code(code, self.__current_state)
            finally:
                self.__remove_state("temp")

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
                f.write(self.__get_code(self.__current_state))
            self.__communicate.show_in_status_bar.emit(
                f"The code of the state {
                    self.__current_state} was saved successfully."
            )
            self.__communicate.print_gui.emit(
                f"The code of the state {
                    self.__current_state} was saved successfully."
            )
        else:
            self.__communicate.show_in_status_bar.emit(
                "No file name is given. The code was not saved."
            )

    def update_to_time(self, t):
        super().update_to_time(t)
        if "first" not in self.__states and self.__starting:
            self.__starting = False
            self.__save_state("first")
        self.__communicate.update_image.emit(self.renderer.get_frame())
