try:
    import openai
except ImportError:
    AIWidget = None
else:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QDialog, QTextEdit, QLabel, QLineEdit, QComboBox
    from PyQt6.QtGui import QIntValidator
    from PyQt6.QtCore import Qt
    from .communicate import Communicate
    from .code_edit import CodeEdit

    SYSTEM_INSTRUCTIONS = "Generate a Python code snippet to generate a Manim animation according to the prompt. " \
        + "The response must contain only one snippet. " \
        + "Never explain the code that you are generating. " \
        + "The code must be valid Python code. " \
        + "The code must not contain any comments. " \
        + "The code must not contain any imports unless it is necessary. " \
        + "Assume you already import Manim and you defined the construct() method of a scene. That means " \
        + "that you won't indent nor write 'from manim import *', nor 'class <SceneName>(Scene):', nor 'def construct(self):'. " \
        + "Your answer must be a code block, it starts with ```python and ends with ```."

    class AIWidget(QWidget):
        """A widget to generate Python code snippets through OpenAI's API."""

        def __init__(self, communicate: Communicate, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.setWindowTitle("Manim Studio - AI Power")
            self.openai_api_key_is_set = False
            self.communicate = communicate
            self.layout_ = QVBoxLayout()
            self.send_code_button = QPushButton("Send code")
            self.send_code_button.clicked.connect(self.send_code)
            response_label = QLabel(text="Response")
            self.response_edit = CodeEdit()
            self.response_edit.setReadOnly(True)
            self.layout_.addWidget(response_label)
            self.layout_.addWidget(self.response_edit)
            self.prompt_edit = QTextEdit()
            self.prompt_edit.setPlaceholderText("Enter the prompt")
            self.layout_.addWidget(self.prompt_edit)
            self.tokens_edit = QLineEdit()
            self.tokens_edit.setValidator(QIntValidator())
            self.tokens_edit.setPlaceholderText(
                "Enter the max tokens (default: 100)")
            self.layout_.addWidget(self.tokens_edit)
            self.send_prompt_button = QPushButton("Send prompt")
            self.send_prompt_button.clicked.connect(self.send_prompt)
            self.select_gpt_version_dropdown = QComboBox()
            self.gpt_version = None
            self.select_gpt_version_dropdown.setPlaceholderText(
                "Select GPT version")
            gpt_dict = {
                "GPT 3.5 Turbo": "gpt-3.5-turbo",
                "GPT 4": "gpt-4"
            }
            self.select_gpt_version_dropdown.addItems(
                ["GPT 3.5 Turbo", "GPT 4"])
            self.select_gpt_version_dropdown.currentIndexChanged.connect(
                lambda: setattr(self, "gpt_version", gpt_dict[self.select_gpt_version_dropdown.currentText()]))
            self.layout_.addWidget(self.send_prompt_button)
            self.layout_.addWidget(self.select_gpt_version_dropdown)
            self.layout_.addWidget(self.send_code_button)
            self.setLayout(self.layout_)
            self.messages = [{"role": "system",
                              "content": SYSTEM_INSTRUCTIONS}]

        def send_prompt(self):
            if self.openai_api_key_is_set is False:
                dialog = QDialog()
                self.api_key_dialog = dialog
                dialog.setWindowTitle("OpenAI API key")
                dialog.layout_ = QVBoxLayout()
                dialog.api_key_edit = QTextEdit()
                dialog.api_key_edit.setPlaceholderText(
                    "Enter your OpenAI API key")
                dialog.layout_.addWidget(dialog.api_key_edit)
                dialog.warn_label = QLabel(
                    text="Please set your OpenAI API key. Once done, send the prompt again.")
                dialog.layout_.addWidget(dialog.warn_label)
                dialog.ok_button = QPushButton("OK")
                dialog.ok_button.clicked.connect(
                    lambda: self.set_api_key(dialog.api_key_edit.toPlainText()))
                dialog.layout_.addWidget(dialog.ok_button)
                dialog.setLayout(dialog.layout_)
                dialog.exec()
                return
            if self.gpt_version is None:
                dialog = QDialog()
                dialog.setWindowTitle("Select GPT version")
                dialog.layout_ = QVBoxLayout()
                dialog.warn_label = QLabel(
                    text="Please select a GPT version. Once done, send the prompt again.")
                dialog.layout_.addWidget(dialog.warn_label)
                dialog.ok_button = QPushButton("OK")
                dialog.ok_button.clicked.connect(
                    lambda: dialog.close())
                dialog.layout_.addWidget(dialog.ok_button)
                dialog.setLayout(dialog.layout_)
                dialog.exec()
                return
            try:
                self.messages.append({"role": "user",
                                      "content": self.prompt_edit.toPlainText()})
                code_completion = openai.ChatCompletion.create(
                    model=self.gpt_version,
                    messages=self.messages,
                    max_tokens=int(self.tokens_edit.text() or 100),
                )
            except openai.OpenAIError as e:
                self.openai_api_key_is_set = False
                self.communicate.alert.emit(e)
            else:
                response = code_completion.choices[0].message.content
                if response.startswith("```python") and response.endswith("```"):
                    response = response[len("```python"): -len("```")]
                self.response_edit.setReadOnly(False)
                self.response_edit.setText(response)

        def send_code(self):
            self.communicate.update_scene.emit(
                self.response_edit.toPlainText())
            self.response_edit.setReadOnly(True)

        def set_api_key(self, api_key: str):
            openai.api_key = api_key
            self.openai_api_key_is_set = True
            self.api_key_dialog.close()
