from __future__ import annotations

from typing import Union, Any
from types import ModuleType, NoneType

import manim

from PyQt6.QtCore import pyqtSignal, QObject


def hold_on(scene: manim.Scene, locals_dict: dict[str, Any]):
    """Hold the scene until the user executes something on Manim Studio."""
    if not ManimStudioAPI.enabled:
        return
    if ManimStudioAPI.scene.deepness > 0:
        ManimStudioAPI.scene.deepness -= 1
        return
    ManimStudioAPI.scope.update(locals_dict)
    if ManimStudioAPI.consider_studio_time:
        frames_waited = 0
    if scene.code:
        ManimStudioAPI.codes.append("")
    while scene.code is None:
        scene.wait(1 / scene.camera.frame_rate, frozen_frame=False)
        if ManimStudioAPI.consider_studio_time:
            frames_waited += 1
    if ManimStudioAPI.consider_studio_time:
        ManimStudioAPI.codes.append(f"self.wait({frames_waited / scene.camera.frame_rate})")
    ManimStudioAPI.execute(scene.code)
    hold_on(scene, {})


class PrintSignalWrapper(QObject):
    """A signal to print text in the GUI."""
    print_signal = pyqtSignal(str)
    show_error_signal = pyqtSignal(Exception)
    

class ManimStudioAPI:
    """The API for Manim Studio"""
    enabled: bool = False
    supported_mobjects: dict[str, type[manim.Mobject]] = {
        "Circle": manim.Circle,
        "Regular Polygon": manim.RegularPolygon,
        "Line": manim.Line,
        "MathTex": manim.MathTex,
        "Text": manim.Text
    }
    consider_studio_time: bool = False
    max_list_length: int = 50

    def __new__(
        cls,
        scene: manim.Scene,
        module: Union[ModuleType, NoneType],
        path_to_file: Union[str, NoneType],
        plugins: list[ModuleType]
    ) -> ManimStudioAPI:
        if not cls.enabled:
            return

        cls.scene = scene
        cls.states_to_undo: list[dict[str, Any]] = []
        cls.states_to_redo: list[dict[str, Any]] = []
        cls.codes_to_redo: list[str] = []
        cls.print_signal_wrapper = PrintSignalWrapper()
        cls.plugins: dict[str, ModuleType] = {}
        cls.scope = globals().copy()
        cls.scope["self"] = scene
        cls.update_scope_with_module(manim)
        cls.path_to_file = path_to_file

        if type(scene) == manim.Scene:
            def new_construct():
                hold_on(scene, {})
            scene.construct = new_construct

        if module is not None:
            cls.update_scope_with_module(module)

        for plugin in plugins:
            cls.add_plugin(plugin)
        
        cls.codes = []

        return super().__new__(cls)

    @classmethod
    def print(cls, *args):
        """Print the given arguments in the GUI."""
        if cls.enabled:
            cls.print_signal_wrapper.print_signal.emit(" ".join(map(str, args)))
        print(*args)
    
    @classmethod
    def execute(cls, code: str):
        """Execute the given code in the scope of the scene.
        
        Warning
        -------
        The code is executed directly. This means that it can be dangerous to
        use this method with untrusted code. Use it at your own risk.
        """
        cls.scene.code = None
        state = cls.scene.__dict__.copy()
        try:
            exec(code, cls.scope)
        except Exception as e:
            cls.scene.__dict__ = state
            cls.print_signal_wrapper.show_error_signal.emit(e)
        else:
            cls.codes.append(code)
            cls.states_to_undo.append(state)
            cls.states_to_redo.clear()
    
    @classmethod
    def undo(cls):
        """Undo the last change in the scene."""
        if len(cls.states_to_undo) == 0:
            return
        cls.states_to_redo.append(cls.scene.__dict__.copy())
        cls.scene.__dict__ = cls.states_to_undo.pop()
        cls.codes_to_redo.append(cls.codes.pop())
        cls.codes_to_redo.append(cls.codes.pop())
        if len(cls.states_to_redo) == cls.max_list_length:
            cls.states_to_redo.pop(0)
    
    @classmethod
    def redo(cls):
        """Redo the last change in the scene."""
        if len(cls.states_to_redo) == 0:
            return
        cls.states_to_undo.append(cls.scene.__dict__.copy())
        cls.scene.__dict__ = cls.states_to_redo.pop()
        cls.codes.append(cls.codes_to_redo.pop())
        cls.codes.append(cls.codes_to_redo.pop())
        if len(cls.states_to_undo) == cls.max_list_length:
            cls.states_to_undo.pop(0)
    
    @classmethod
    def update_scope_with_module(cls, module: ModuleType):
        """Update the scope of the scene with the given module.
        It is useful to add new variables or functions that you want to use.
        """
        cls.scope.update(module.__dict__)
    
    @classmethod
    def is_in_scope(cls, name: str):
        """Return whether the given name is in the scope of the scene."""
        return name in cls.scope
    
    @classmethod
    def add_plugin(
        cls,
        plugin: ModuleType
    ):
        """Add a plugin to Manim Studio application.
        
        Parameters
        ----------
        plugin : ModuleType
            The module of the plugin to add. It must contain a :code:`main` function
            that will be called with the API as the only argument."""
        if not hasattr(plugin, "main"):
            raise ValueError("The plugin must have a 'main' function")
        if not callable(plugin.main):
            raise ValueError("The 'main' function of the plugin must be callable")
        if plugin.main.__code__.co_argcount != 1:
            raise ValueError("The 'main' function of the plugin must take exactly one argument")
        cls.plugins[plugin.__name__] = plugin
    
    @classmethod
    def run_plugin(
        cls,
        plugin_name: str
    ):
        """Run the plugin with the given name."""
        if plugin_name not in cls.plugins:
            raise ValueError(f"The plugin '{plugin_name}' does not exist")
        cls.plugins[plugin_name].main(cls)
    
    @classmethod
    def get_all_code(cls):
        """Return all the code executed in the application."""
        return "\n".join(cls.codes)
