from manim_studio import *
from manim import *
from time import sleep


class DropdownExample(LiveScene):
    def construct(self):
        self.add_dropdown_command(
            "dropdown", ["np.cos", "np.sin", "np.exp", "np.log", "np.sqrt"])
        sleep(1)  # wait for the dropdown widget to be created

        def get_domain(func):
            if func == "np.log":
                return [np.exp(-config.frame_y_radius), config.frame_x_radius]
            elif func == "np.sqrt":
                return [0, config.frame_x_radius]
            else:
                return [-config.frame_x_radius, config.frame_x_radius]

        def updater(graph):
            func = eval(self.dropdown.get_value())
            graph.become(FunctionGraph(
                func, color=YELLOW, x_range=get_domain(self.dropdown.get_value())))

        plane = NumberPlane()
        graph = VMobject().add_updater(updater)

        self.play(Write(plane))
        self.add(graph)

        super().construct()


if __name__ == "__main__":
    run_manim_studio(DropdownExample)
