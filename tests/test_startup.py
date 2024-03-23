import subprocess
import sys


class TestStartup:
    def test_startup(self):
        subprocess.run([sys.executable, "-m", "manim_studio",
                       "--timeout", "5"], check=True)
