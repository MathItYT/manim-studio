import subprocess
import sys


class TestStartup:
    def test_startup(self):
        print(f"Testing on version {sys.version}")
        subprocess.run([sys.executable, "-m", "manim_studio",
                       "--timeout", "5"], check=True)
