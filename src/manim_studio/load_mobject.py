import dill as pickle


def load_mobject(file_name):
    """Load a mobject from a file."""
    with open(file_name, "rb") as f:
        return pickle.load(f)
