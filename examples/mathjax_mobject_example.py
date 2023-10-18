from manim_studio import *
from manim import *
from time import sleep


class MathJaxExample(LiveScene):
    def construct(self):
        self.current_code = "self.x_times_1000 = IntValueTracker(0)"
        self.run_instruction()

        self.add_slider_command("x_times_1000", "0", "0", "10000", "10")
        sleep(1)  # Wait for the slider to be added to the scene
        self.current_code = "current_x = 0.0"
        self.run_instruction()

        self.current_code = """
def updater(mobject: MathJax):
    global current_x
    if self.x_times_1000.get_value() / 1000 != current_x:
        current_x = self.x_times_1000.get_value() / 1000
        mobject.become(MathJax(
            f"{mobject.get_colored_expr('x', YELLOW)} = {mobject.get_colored_expr(f'{current_x:.2f}', BLUE)}"))
"""
        self.run_instruction()

        self.current_code = """mathjax = MathJax("x = 0.00")\n"""
        self.current_code += """mathjax.add_updater(updater)\n"""
        self.current_code += """self.add(mathjax)"""
        self.run_instruction()

        super().construct()
