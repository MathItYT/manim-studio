from manim import logger, config, SVGMobject, VMobject, color_to_rgb
from colour import Color
from manim.utils.tex_file_writing import tex_hash
import inspect
import importlib
from pathlib import Path
import subprocess
import re


def create_dir_if_not_exists(dir_path: Path):
    if not dir_path.exists():
        dir_path.mkdir(parents=True)


def check_nodejs_installation():
    try:
        subprocess.run(["node", "--version"], check=True)
    except FileNotFoundError:
        raise FileNotFoundError(
            "Node.js is not installed. Please install node and try again.")
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "Node.js is not installed correctly. Please install node and try again.")


def get_cli_path():
    module = importlib.import_module(
        "manim_studio.mathjax_mobject.mathjax_mobject")
    folder = Path(inspect.getfile(module)).parent
    return (folder / "mathjax-cli.js").absolute()


def install_dependencies_if_not_installed():
    logger.info("Checking if manim-mathjax is installed...")
    logger.info("Installing manim-mathjax...")
    try:
        subprocess.run(
            ["npm", "install", get_cli_path().parent], check=True, shell=True)
    except FileNotFoundError:
        raise FileNotFoundError(
            "NPM is not installed. Please install npm and try again.")
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "An error occurred while installing manim-mathjax. Please try again.")
    logger.info("manim-mathjax is installed.")


def render_mathjax(mathjax_str: str, check_installation=True):
    """Render a MathJax string as a mobject.

    Solution from https://github.com/manim-kindergarten/ManimGL-MathJax/blob/main/manimgl_mathjax/mathjax.py

    Parameters
    ----------
    mathjax_str : str
        A MathJax string.
    **kwargs
        Keyword arguments to pass to the MathTex mobject.

    Returns
    -------
    MathTex
        A MathTex mobject.
    """
    if check_installation:
        check_nodejs_installation()
        install_dependencies_if_not_installed()
    cli_path = get_cli_path()
    p = subprocess.Popen(["node", str(cli_path)],
                         stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate(input=mathjax_str.encode("utf-8"))
    svg_str = out.decode("utf-8")

    error_match_obj = re.search(
        r"(?<=data\-mjx\-error\=\")(.*?)(?=\")", svg_str)
    if error_match_obj is not None:
        logger.error(
            "LaTeX Error!  Not a worry, it happens to the best of us.")
        logger.info(f"The error could be: `{error_match_obj.group()}`")
        raise ValueError("LaTeX Error")
    tex_dir = config.get_dir("tex_dir")
    tex_file = tex_dir / f"{tex_hash(mathjax_str)}.svg"
    create_dir_if_not_exists(config.get_dir("media_dir"))
    create_dir_if_not_exists(tex_dir)
    with open(tex_file, "wb") as f:
        f.write(out)
    return tex_file


class MathJax(SVGMobject):
    first_time = True

    def __init__(self, expr: str, font_size: int = 48, color=None, opacity=None, stroke_width=None, **kwargs):
        self.expr = expr
        self.font_size = font_size
        if color is None:
            color = VMobject().color
        if opacity is None:
            opacity = 1.0
        if stroke_width is None:
            stroke_width = 0.0
        self.colored_expr = self.get_colored_expr(self.expr, color)
        super().__init__(render_mathjax(self.colored_expr, self.__class__.first_time), **kwargs)
        self.__class__.first_time = False
        self.set_color(color, family=False)
        self.set_opacity(opacity)
        self.set_stroke(width=stroke_width)
        self.scale(0.2 * self.font_size / 48)

    def get_colored_expr(self, expr: str, color: Color):
        return f"\\textcolor[rgb]{{{','.join(map(str, color_to_rgb(color)))}}}{{{expr}}}"
