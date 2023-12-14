from PyQt6.QtCore import pyqtSignal, QObject
from manim import Mobject
import numpy as np


class Communicate(QObject):
    """A class to communicate using signals and slots."""

    update_scene = pyqtSignal(str)
    update_image = pyqtSignal(np.ndarray)
    show_in_status_bar = pyqtSignal(str)
    print_gui = pyqtSignal(str)
    save_to_python = pyqtSignal()
    save_state = pyqtSignal()
    undo_state = pyqtSignal()
    redo_state = pyqtSignal()
    add_value_tracker = pyqtSignal(str, Mobject)
    save_mobject = pyqtSignal()
    load_mobject = pyqtSignal()
    enable_interact = pyqtSignal(bool)
    add_to_interactive_mobjects = pyqtSignal(str)
    remove_from_interactive_mobjects = pyqtSignal(str)
