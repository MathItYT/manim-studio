from manim import Mobject
import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy

jsonpickle_numpy.register_handlers()

try:
    import pandas as pd
except ImportError:
    pass
else:
    import jsonpickle.ext.pandas as jsonpickle_pandas
    jsonpickle_pandas.register_handlers()

try:
    import gmpy2
except ImportError:
    pass
else:
    import jsonpickle.ext.gmpy as jsonpickle_gmpy
    jsonpickle_gmpy.register_handlers()


def save_mobject(mobject: Mobject, file_name: str):
    """Save a mobject to a file."""
    with open(file_name, "w") as f:
        json_str = jsonpickle.encode(mobject, unpicklable=False)
        f.write(json_str)


def load_mobject(file_name: str) -> Mobject:
    """Load a mobject from a file."""
    with open(file_name, "r") as f:
        json_str = f.read()
        mobject = jsonpickle.decode(json_str)
    return mobject
