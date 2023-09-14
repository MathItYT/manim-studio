from manim_studio import *
from manim import *
from time import sleep


class TextEditExample(LiveScene):
    def construct(self):
        self.add_text_editor_command("text_editor", "Hello, World!")
        sleep(1)  # wait for the text editor widget to be created

        def updater(text):
            text.become(Paragraph(*self.text_editor.get_value().split("\n")))
            text.scale_to_fit_width(min(config.frame_width, text.width))

        text = VMobject().add_updater(updater)
        self.add(text)

        super().construct()


if __name__ == "__main__":
    run_manim_studio(TextEditExample)
