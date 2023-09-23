from manim_studio import *
from manim import *
from time import sleep


class TextEditExample(LiveScene):
    def construct(self):
        self.add_text_editor_command("text_editor", "Hello, World!")
        sleep(1)  # wait for the text editor widget to be created

        paragraph = Paragraph("Hello, World!")
        content = self.text_editor.get_value()

        def update_paragraph(m):
            nonlocal content
            if content != self.text_editor.get_value():
                content = self.text_editor.get_value()
                m.become(Paragraph(*content.split("\n")))

        self.add(paragraph)
        paragraph.add_updater(update_paragraph)

        super().construct()


if __name__ == "__main__":
    run_manim_studio(TextEditExample)
