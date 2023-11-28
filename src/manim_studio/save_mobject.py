from manim import Mobject
import dill as pickle


def transform_type(mobject: Mobject):
    type_class = mobject.get_mobject_type_class()()
    if type_class != Mobject:
        return type_class.become(mobject)
    result = type_class
    for submob in mobject.submobjects:
        result.add(transform_type(submob))
    return result


def save_mobject(mobject: Mobject, file_name: str):
    """
    Save a mobject to a file.

    Warning
    -------
    The result mobject doesn't look different from the original one, but this
    and its submobjects are of different types, specifically their base classes.
    """
    result = transform_type(mobject)
    with open(file_name, "wb") as f:
        pickle.dump(result, f)
