import subprocess


class TestStartup:
    def test_startup(self):
        subprocess.run(["python3", "-m", "manim_studio",
                       "--timeout", "5"], check=True)
