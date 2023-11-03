from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QColor, QFont


class CodeEdit(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUtf8(True)
        self.code_lexer = QsciLexerPython()
        self.code_lexer.setDefaultFont(QFont("Consolas", 12))
        self.code_lexer.setDefaultPaper(QColor("#272822"))
        self.code_lexer.setDefaultColor(QColor("#F8F8F2"))
        self.code_lexer.setColor(QColor("#75715E"), QsciLexerPython.Comment)
        self.code_lexer.setColor(QColor("#75715E"),
                                 QsciLexerPython.CommentBlock)
        self.code_lexer.setColor(QColor("#F92672"),
                                 QsciLexerPython.Keyword)
        # Numbers purple
        self.code_lexer.setColor(QColor("#AE81FF"),
                                 QsciLexerPython.Number)
        # Strings orange
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.DoubleQuotedString)
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.SingleQuotedString)
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.TripleSingleQuotedString)
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.TripleDoubleQuotedString)
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.DoubleQuotedFString)
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.SingleQuotedFString)
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.TripleSingleQuotedFString)
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.TripleDoubleQuotedFString)
        # Unclosed string red
        self.code_lexer.setColor(QColor("#F92672"),
                                 QsciLexerPython.UnclosedString)
        # Functions yellow
        self.code_lexer.setColor(QColor("#E6DB74"),
                                 QsciLexerPython.FunctionMethodName)
        # Classes green
        self.code_lexer.setColor(QColor("#A6E22E"),
                                 QsciLexerPython.ClassName)
        # Operators red
        self.code_lexer.setColor(QColor("#F92672"),
                                 QsciLexerPython.Operator)
        # Highlighted identifiers blue
        self.code_lexer.setColor(QColor("#66D9EF"),
                                 QsciLexerPython.HighlightedIdentifier)
        # Decorators blue
        self.code_lexer.setColor(QColor("#66D9EF"),
                                 QsciLexerPython.Decorator)
        # Set tab width to 4 spaces
        self.setTabWidth(4)
        self.setTabIndents(True)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationGuides(True)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.DoubleQuotedFString)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.SingleQuotedFString)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.TripleDoubleQuotedFString)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.TripleSingleQuotedFString)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.DoubleQuotedString)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.SingleQuotedString)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.TripleDoubleQuotedString)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.TripleSingleQuotedString)
        self.code_lexer.setFont(QFont("Consolas", 12),
                                QsciLexerPython.UnclosedString)
        self.setLexer(self.code_lexer)
        self.setMarginsBackgroundColor(QColor("#272822"))
        self.setMarginsForegroundColor(QColor("#F8F8F2"))
        self.setCaretForegroundColor(QColor("#F8F8F2"))
        self.setGeometry(0, 0, 100, 50)

    def toPlainText(self):
        return self.text()
