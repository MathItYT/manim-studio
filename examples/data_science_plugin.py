from manim_studio import ManimStudioAPI
from manim_studio.window import Window
from manim_studio.input_widgets.range_slider import RangeSlider


CODE = "self.generate_points(int(self.n), self.noise_factor)"


def main(cls: type[ManimStudioAPI]):
    print("Hello from Data Science Plugin for Manim Studio!")


def init_widgets(window: Window):
    n_slider = RangeSlider("n", 100, 1, 1000, 1, window.width())
    n_slider.expression_editor.setPlainText(CODE)
    n_slider.expression_editor.setDisabled(True)
    n_slider.expression_selector.setDisabled(True)
    noise_factor_slider = RangeSlider("noise_factor", 0.5, 0, 1, 0.01, window.width())
    noise_factor_slider.expression_editor.setPlainText(CODE)
    noise_factor_slider.expression_editor.setDisabled(True)
    noise_factor_slider.expression_selector.setDisabled(True)
    window.input_widgets_zone.widget().layout().addWidget(n_slider)
    window.input_widgets_zone.widget().layout().addWidget(noise_factor_slider)
