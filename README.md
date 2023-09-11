# Manim Studio

![Manim Studio](https://raw.githubusercontent.com/MathItYT/manim-studio/main/logo.png)

Manim Studio is a Manim plugin to live-preview animations rendered with Cairo, and also it's useful for many other things!

## Features
- [x] Live preview for Cairo animations.
- [x] Saving and loading snippets.
- [x] Saving full scene snipets.
- [ ] Create slides with Manim Studio.
- [ ] Basic editing for Manim videos.
- [ ] Direct livestreaming with OBS.
- [ ] Snippet gallery.

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

2. Use the program! We still don't have a documentation, but there will be one in the future!


## Examples

1. **Basic example**
   
   ```python
   from manim_studio import *


   if __name__ == "__main__":
       run_manim_studio(LiveScene)
   ```

2. **Example with initial part**
   
   ```python
   from manim_studio import *


   class InitialPartExample(LiveScene):
       def construct(self):
           txt = Tex("Hello world!")
           self.play(Write(txt))
           self.wait()
           play_with_this = Tex("Play with the GUI!")
           self.play(FadeIn(play_with_this))
           self.wait()
           
           super().construct()
   ```
