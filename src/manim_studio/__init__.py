from .main import main as run_manim_studio
from .live_scene import LiveScene
from .load_snippet import load_snippet
from .prerender_latex import prerender_latex
from .value_trackers.int_value_tracker import IntValueTracker
from .value_trackers.color_value_tracker import ColorValueTracker
from .value_trackers.string_value_tracker import StringValueTracker
from .value_trackers.boolean_value_tracker import BooleanValueTracker
from .mathjax_mobject.mathjax_mobject import MathJax
from .saving_and_loading_mobjects import save_mobject, load_mobject
from pkg_resources import get_distribution


__version__ = get_distribution("manim-studio").version
