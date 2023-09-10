from manim import *
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QMessageBox
from time import sleep

from communicate import Communicate


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

    def construct(self):
        while True:
            while self.no_instruction():
                sleep(1.0)
            try:
                scope = globals()
                scope["self"] = self
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

    def wait(self, *args, frozen_frame=False, **kwargs):
        super().wait(*args, frozen_frame=frozen_frame, **kwargs)

    @pyqtSlot(str)
    def update_scene(self, code: str):
        self.current_code = code

    @pyqtSlot()
    def end_scene(self):
        self.current_code = "raise EndSceneEarlyException()"

    @pyqtSlot(Exception)
    def alert(self, e: Exception):
        alert = QMessageBox(
            text="An error occured while processing your code.")
        alert.setWindowTitle("Error")
        alert.setIcon(QMessageBox.Icon.Warning)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.setInformativeText(f"{e.__class__.__name__}: {e}")
        alert.exec()

    def no_instruction(self):
        return self.current_code is None
