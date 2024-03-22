import subprocess


class TestStartup:
    def test_startup(self):
        subprocess.run(["manim-studio", "--timeout", "5"], check=True)
