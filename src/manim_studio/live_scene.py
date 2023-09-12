from manim import *
from PyQt6.QtCore import QObject, pyqtSlot, Qt
from PyQt6.QtWidgets import QMessageBox, QSlider, QWidget

from .communicate import Communicate
from .int_value_tracker import IntValueTracker


class CairoLiveRenderer(QObject, CairoRenderer):
    def __init__(self, communicate: Communicate, *args, **kwargs):
        QObject.__init__(self)
        CairoRenderer.__init__(self, *args, **kwargs)
        self.communicate = communicate

    def render(self, scene, time, moving_mobjects):
        super().render(scene, time, moving_mobjects)
        self.communicate.update_image.emit(self.get_frame())


class LiveScene(QObject, Scene):
    def __init__(self, communicate: Communicate, renderer=None, *args, **kwargs):
        config.disable_caching = True
        QObject.__init__(self)
        Scene.__init__(self, *args, **kwargs)
        self.communicate = communicate
        renderer = CairoLiveRenderer(communicate)
        QObject.__init__(self)
        Scene.__init__(self, renderer=renderer, *args, **kwargs)
        self.communicate.update_scene.connect(self.update_scene)
        self.communicate.end_scene.connect(self.end_scene)
        self.communicate.alert.connect(self.alert)
        self.current_code = None
        self.codes = []
        self.sliders = dict()
        self.freeze = False

    def construct(self):
        while True:
            while self.no_instruction():
                self.wait()
            try:
                scope = globals()
                scope.update(locals())
                exec(self.current_code, scope)
            except EndSceneEarlyException:
                raise EndSceneEarlyException()
            except Exception as e:
                logger.info(
                    f"Exception occured in live scene: {e}")
                self.communicate.alert.emit(e)
            else:
                self.codes.append(self.current_code)
            self.current_code = None

    def add_slider_command(self, name: str, default_value: str, min_value: str, max_value: str, step_value: str):
        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_value))
        slider.setMaximum(int(max_value))
        slider.setValue(int(default_value))
        slider.setSingleStep(int(step_value))
        slider.valueTracker = IntValueTracker(slider.value())
        slider.valueChanged.connect(slider.valueTracker.set_value)
        self.sliders[name] = slider
        setattr(self, name, slider.valueTracker)
        self.add(slider.valueTracker)
        self.communicate.add_slider_to_editor.emit(name)

    def wait(self, *args, frozen_frame=False, **kwargs):
        super().wait(*args, frozen_frame=frozen_frame, **kwargs)

    @pyqtSlot(str)
    def update_scene(self, code: str):
        if self.freeze:
            alert = QMessageBox(
                text="You cannot update the scene while it is paused.")
            alert.setWindowTitle("Scene paused")
            alert.setIcon(QMessageBox.Icon.Information)
            alert.setStandardButtons(QMessageBox.StandardButton.Ok)
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
        while self.freeze:
            self.wait()

    def no_instruction(self):
        return self.current_code is None
