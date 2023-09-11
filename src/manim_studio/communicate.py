from PyQt6.QtCore import pyqtSignal, QObject
import numpy as np


class Communicate(QObject):
    update_scene = pyqtSignal(str)
    update_image = pyqtSignal(np.ndarray)
    end_scene = pyqtSignal()
    alert = pyqtSignal(Exception)
    save_snippet = pyqtSignal(str)
