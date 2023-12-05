import dill as pickle


def save_mobject(mobject, path, scope):
    self = scope["self"]
    scope["self"] = None
    with open(path, "wb") as f:
        pickle.dump(mobject, f)
    scope["self"] = self
