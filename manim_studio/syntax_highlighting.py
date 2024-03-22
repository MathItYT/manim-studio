from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import QRegularExpression


class PythonHighlighter(QSyntaxHighlighter):
    """A syntax highlighter for Python code."""

    def highlightBlock(self, text: str):
        self.light(text)
        self.highlight_numbers(text)
        self.highlight_keywords(text)
        self.highlight_strings(text)
        self.highlight_comments(text)

    def light(self, text: str):
        light_format = QTextCharFormat()
        light_format.setForeground(QColor(214, 214, 214))
        light_format.setFontFamily("Consolas")
        light_format.setFontPointSize(16)
        light_format.setFontWeight(150)
        self.highlight(QRegularExpression(r"."), light_format, text)

    def highlight_numbers(self, text: str):
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(180, 210, 115))
        number_format.setFontFamily("Consolas")
        number_format.setFontPointSize(16)
        number_format.setFontWeight(150)
        self.highlight(QRegularExpression(r"\b[0-9]+\b"), number_format, text)

    def highlight_keywords(self, text: str):
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(176, 82, 121))
        keyword_format.setFontFamily("Consolas")
        keyword_format.setFontPointSize(16)
        keyword_format.setFontWeight(150)
        self.highlight(QRegularExpression(
            r"\b("
            r"and|as|assert|async|await"
            r"|break|class|continue|def|"
            r"del|elif|else|except|finally|"
            r"for|from|global|if|import|in|"
            r"is|lambda|nonlocal|not|or"
            r"|pass|raise|return|try|while"
            r"|with|yield|self|super|True|"
            r"False|None|print|input|open|"
            r"range|len|list|dict|set|tuple|"
            r"int|float|str|bool|complex|"
            r"abs|all|any|ascii|bin|bool|"
            r"bytes|callable|chr|classmethod|"
            r"compile|complex|delattr|dict|"
            r"dir|divmod|enumerate|eval|"
            r"exec|filter|float|format|frozenset|"
            r"getattr|globals|hasattr|hash|"
            r"help|hex|id|input|int|isinstance|"
            r"issubclass|iter|len|list|locals|"
            r"map|max|memoryview|min|next|"
            r"object|oct|open|ord|pow|print|"
            r"property|range|repr|reversed|"
            r"round|set|setattr|slice|sorted|"
            r"staticmethod|str|sum|super|tuple|"
            r"type|vars|zip"
            r")\b"
        ), keyword_format, text)

    def highlight_strings(self, text: str):
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))
        string_format.setFontFamily("Consolas")
        string_format.setFontPointSize(16)
        string_format.setFontWeight(150)
        self.highlight(QRegularExpression(r"\".*\""), string_format, text)
        self.highlight(QRegularExpression(r"'.*'"), string_format, text)

    def highlight_comments(self, text: str):
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(100, 100, 100))
        comment_format.setFontFamily("Consolas")
        comment_format.setFontPointSize(16)
        comment_format.setFontWeight(150)
        self.highlight(QRegularExpression(r"#.*"), comment_format, text)

    def highlight(self, pattern: QRegularExpression, char_format: QTextCharFormat, text: str):
        match = pattern.match(text)
        while match.hasMatch():
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(start, length, char_format)
            match = pattern.match(text, start + length)
