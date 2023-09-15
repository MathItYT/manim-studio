from pathlib import Path
from manim import logger
import subprocess


BUILTINS_REPO = "https://github.com/MathItYT/manim-studio-snippets.git"


def main():
    if not Path("builtin_snippets").exists():
        subprocess.run(
            [
                "git",
                "clone",
                BUILTINS_REPO,
                "builtin_snippets",
            ],
            check=True,
        )
    else:
        logger.error(
            "If you want to initialize built-in snippets, please delete the builtins_snippets folder and try again!"
        )
        exit(1)
