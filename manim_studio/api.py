from typing import Union
from types import ModuleType, NoneType
import time

import manim

from PyQt6.QtWidgets import QMessageBox


def hold_on(scene: manim.Scene):
    """Hold the scene until the user executes something on Manim Studio."""
    if not ManimStudioAPI.enabled:
        return
    scene.code = None
    last_time = time.time()
    while scene.code is None:
        dt = time.time() - last_time
        scene.wait(dt, frozen_frame=False)
        last_time = time.time()
    ManimStudioAPI.execute(scene.code)
    hold_on(scene)


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

    def __new__(
        cls,
        scene: manim.Scene,
        module: Union[ModuleType, NoneType],
        path_to_file: Union[str, NoneType],
        plugins: list[ModuleType]
    ):
        if not cls.enabled:
            return

        cls.scene = scene
        cls.plugins: dict[str, ModuleType] = {}
        cls.scope = globals().copy()
        cls.scope["self"] = scene
        cls.update_scope_with_module(manim)
        cls.path_to_file = path_to_file

        if type(scene) == manim.Scene:
            def new_construct():
                hold_on(scene)
            scene.construct = new_construct

        if module is not None:
            cls.update_scope_with_module(module)

        for plugin in plugins:
            cls.add_plugin(plugin)
        
        cls.codes = []

        return super().__new__(cls)
    
    @classmethod
    def execute(cls, code: str):
        """Execute the given code in the scope of the scene.
        
        Warning
        -------
        The code is executed directly. This means that it can be dangerous to
        use this method with untrusted code. Use it at your own risk.
        """
        state = cls.scene.__dict__.copy()
        try:
            exec(code, cls.scope)
        except Exception as e:
            cls.scene.__dict__ = state
            cls.show_error(e)
        else:
            cls.codes.append(code)
    
    @classmethod
    def show_error(cls, error: Exception):
        """Show the given error in the GUI."""
        QMessageBox.critical(
            None,
            "Error",
            "¡Ha ocurrido un error!\n\n"
            f"{error.__class__.__name__}: {error}"
        )
    
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
