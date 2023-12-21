from manim_studio.communicate import Communicate
from manim_studio.editor_widget import EditorWidget
from manim_studio.preview_widget import PreviewWidget
from manim_studio.render_thread import RenderThread
from manim_studio.live_scene import LiveScene
from PyQt6.QtWidgets import QApplication, QDialog, QTextEdit, QVBoxLayout, QLabel, QPushButton
from .controls_widget import ControlsWidget
from .inherits_dialog import InheritsDialog
from manim import config, Scene
import sys
import argparse
from manim_studio.import_from_file import import_from_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write_to_movie", "-w",
                        action="store_true", default=False)
    parser.add_argument("--file_name", "-f", type=str, default="none")
    parser.add_argument("--consider_manim_studio_time", "-c",
                        action="store_true", default=False)
    parser.add_argument("--resolution", "-r", type=str, default="1920x1080")
    parser.add_argument("--fps", "-fps", type=int, default=60)
    parser.add_argument("--include_secrets", "-s", action="store_true", default=False)
    parser.add_argument("--scene_name", "-sn", type=str, default="None")
    args = parser.parse_args()
    if args.file_name != "none":
        module = import_from_file(args.file_name)
    else:
        module = None
    config.write_to_movie = args.write_to_movie
    config.frame_rate = args.fps
    config.disable_caching = True
    width, height = args.resolution.split("x")
    config.pixel_width, config.pixel_height = int(width), int(height)
    max_dimension = max(config.pixel_width, config.pixel_height)
    if max_dimension == config.pixel_width:
        config.frame_width = int(config.pixel_width / config.pixel_height * 8)
        config.frame_height = 8
    else:
        config.frame_height = int(config.pixel_height / config.pixel_width * 8)
        config.frame_width = 8
    app = QApplication([])
    size = app.primaryScreen().size()
    size = (size.width(), size.height())
    if args.scene_name == "None":
        inherits_dialog = InheritsDialog(
            module, args.consider_manim_studio_time, args.include_secrets)
        inherits_dialog.exec()
        communicate = Communicate()
        controls_widget = ControlsWidget()
        scene = inherits_dialog.get_scene(communicate)
    else:
        communicate = Communicate()
        controls_widget = ControlsWidget()
        scene_class = getattr(module, args.scene_name)
        mro_without_live_scene = [scene_type for scene_type in scene_class.__mro__ if not issubclass(
            scene_type, LiveScene)] or [Scene]
        if args.include_secrets:
            secrets_dialog = QDialog()
            secrets_dialog.setModal(True)
            secrets_dialog.setWindowTitle("Secrets")
            secrets_dialog.setLayout(QVBoxLayout())
            secrets_dialog.layout().addWidget(QLabel(
                "Put all your secrets as 'key=value' pairs in the text box below, separated by newlines."))
            secrets_text_box = QTextEdit()
            secrets_dialog.layout().addWidget(secrets_text_box)
            ok_button = QPushButton("OK")
            ok_button.clicked.connect(secrets_dialog.accept)
            secrets_dialog.layout().addWidget(ok_button)
            secrets_dialog.exec()
            if secrets_dialog.result() != QDialog.DialogCode.Accepted:
                return
            secrets = secrets_text_box.toPlainText().split("\n")
            secrets = {secret.split("=")[0]: secret.split("=")[1]
                       for secret in secrets}
        else:
            secrets = {}
        scene = scene_class(communicate=communicate, mro_without_live_scene=mro_without_live_scene, module=module, consider_manim_studio_time=args.consider_manim_studio_time, secrets=secrets)
    if scene is None:
        return
    editor_widget = EditorWidget(
        communicate, controls_widget, scene)
    render_thread = RenderThread(scene)
    preview_widget = PreviewWidget(communicate, size, render_thread)
    render_thread.start()
    preview_widget.show()
    editor_widget.show()
    controls_widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
