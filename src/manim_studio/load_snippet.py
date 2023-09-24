def load_snippet(scene, file_name):
    with open(file_name, "r") as f:
        code = f.read()
    scope = globals()
    scope["self"] = scene
    exec(code, scope)
