# Manim Studio

[![Deploy static content to Pages](https://github.com/MathItYT/manim-studio/actions/workflows/static.yml/badge.svg)](https://github.com/MathItYT/manim-studio/actions/workflows/static.yml)

![Manim Studio](https://raw.githubusercontent.com/MathItYT/manim-studio/main/logo.png)

Manim Studio is a Manim plugin to live-preview animations rendered with Cairo, and also it's useful for many other things!

## Features
- [x] Live preview Manim animations made with Cairo.
- [x] Work with Manim Mobject using the GUI.
- [x] Export to a Python file the code of the animation.
- [x] A live cell to interactively insert code into the scene.
- [ ] Create animations with the GUI.
- [ ] Create animations with AI.
- [ ] Collaborate with other people in the same project.

## Requirements to install
### Install with `git`
- Installed Python 3.
- Installed Manim.
- Installed PyQt6.
- Installed Git.

### Install with `pip`
`pip` installs all the requirements automatically, but you must have installed Python 3.

## Steps to use
1. If you're installing with `git`, clone the repository with
   
   ```
   git clone https://github.com/MathItYT/manim-studio.git
   cd manim-studio
   pip install -e .
   ```
   
   If you're installing with `pip`, install the package with
   
   ```pip install manim-studio```

   Additionally, you can install an extra to create AI-powered animations with
   
   ```pip install manim-studio[ai]```

   It has direct integration with OpenAI API, so you must have an API key to use it.

2. Use the program! The documentation is available [here](https://mathityt.github.io/manim-studio/).

   **Warning:** The documentation is a work in progress, so it may not be complete. ⚠️


## Manim Studio Client
We removed the Manim Studio Client as an standalone application because anti-virus programs detected it as a virus. You can still use it by installing Manim Studio with `pip` and running `manim-studio -C` in the command line.

## Contributing
If you want to contribute to Manim Studio, you can do it by forking the repository and making a pull request. You can also contribute by reporting bugs or suggesting new features.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.
