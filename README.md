# Manim Studio

![Manim Studio](https://raw.githubusercontent.com/MathItYT/manim-studio/main/logo.png)

Manim Studio is a Manim plugin to live-preview animations rendered with Cairo, and also it's useful for many other things!

## Features
- [x] Live preview Manim animations made with Cairo.
- [x] Work with Manim Mobject using the GUI.
- [x] Export to a Python file the code of the animation.
- [x] A live cell to interactively insert code into the scene.
- [x] Create animations with the GUI.
- [ ] Create animations with AI.
- [ ] Collaborate with other people in the same project.

## Requirements to install
### Install with `git`
- Installed Python 3.
- Installed Manim.
- Installed PyQt6.
- Installed Git.

### Install with `pip`
`pip` installs all the requirements automatically, but you must have Python 3 installed.

## Steps to use
The documentation is not available by the moment, but it will be soon.

You can run Manim Studio in a new scene, but also in a scene that you've been working before with code.

If you want to work in a completely new scene, you must run:

```console
foo@bar:~$ manim-studio
```

If you want to work in a scene that you've been working before with code,
you must run:

```console
foo@bar:~$ manim-studio --file FILE --scene SCENE_CLASS_NAME
```

To save your progress, you must click on `Generate Python File` button.

If you want to continue later, you must save your progress and
run Manim Studio using the generated Python file and its respective
scene class.

You can also render a video by clicking `Render Video File`.

## Contributing
If you want to contribute to Manim Studio, you can do it by forking the repository and making a pull request. You can also contribute by reporting bugs or suggesting new features.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.
