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
    save_state = pyqtSignal(str)
    restore_state = pyqtSignal(str)
    remove_state = pyqtSignal(str)
    add_value_tracker = pyqtSignal(str, Mobject)
