import dill as pickle


def load_mobject(path):
    with open(path, "rb") as f:
        return pickle.load(f)
