from manim_studio import *
from manim import *
from time import sleep


class LineEditExample(LiveScene):
    def construct(self):
        self.add_line_edit_command("line_edit", "Hello, World!")
        sleep(1)  # wait for the line edit widget to be created

        def updater(text):
            text.become(Text(self.line_edit.get_value()))

        text = VMobject().add_updater(updater)
        self.add(text)

        super().construct()
