from mau.lexers.base_lexer import TokenTypes
from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer
from mau.text_buffer.text_buffer import TextBuffer
from mau.tokens.tokens import Token


def test_normal_text():
    text_buffer = TextBuffer("Some text")
    lex = PreprocessVariablesLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "S"),
        Token(TokenTypes.TEXT, "o"),
        Token(TokenTypes.TEXT, "m"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "x"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.EOL),
    ]


def test_match_only_backticks_and_curly_braces():
    text_buffer = TextBuffer("Normal text `{curly}` _other_ *text*")
    lex = PreprocessVariablesLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "N"),
        Token(TokenTypes.TEXT, "o"),
        Token(TokenTypes.TEXT, "r"),
        Token(TokenTypes.TEXT, "m"),
        Token(TokenTypes.TEXT, "a"),
        Token(TokenTypes.TEXT, "l"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "x"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.LITERAL, "`"),
        Token(TokenTypes.LITERAL, "{"),
        Token(TokenTypes.TEXT, "c"),
        Token(TokenTypes.TEXT, "u"),
        Token(TokenTypes.TEXT, "r"),
        Token(TokenTypes.TEXT, "l"),
        Token(TokenTypes.TEXT, "y"),
        Token(TokenTypes.LITERAL, "}"),
        Token(TokenTypes.LITERAL, "`"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "_"),
        Token(TokenTypes.TEXT, "o"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "h"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "r"),
        Token(TokenTypes.TEXT, "_"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "*"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "x"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "*"),
        Token(TokenTypes.EOL),
    ]


def test_escape_curly_braces():
    text_buffer = TextBuffer(r"Normal text \{curly\} _other_ *text*")
    lex = PreprocessVariablesLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "N"),
        Token(TokenTypes.TEXT, "o"),
        Token(TokenTypes.TEXT, "r"),
        Token(TokenTypes.TEXT, "m"),
        Token(TokenTypes.TEXT, "a"),
        Token(TokenTypes.TEXT, "l"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "x"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "{"),
        Token(TokenTypes.TEXT, "c"),
        Token(TokenTypes.TEXT, "u"),
        Token(TokenTypes.TEXT, "r"),
        Token(TokenTypes.TEXT, "l"),
        Token(TokenTypes.TEXT, "y"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "}"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "_"),
        Token(TokenTypes.TEXT, "o"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "h"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "r"),
        Token(TokenTypes.TEXT, "_"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "*"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "x"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "*"),
        Token(TokenTypes.EOL),
    ]


def test_preserve_escapes():
    text_buffer = TextBuffer(r"Normal \text \_other\_")
    lex = PreprocessVariablesLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "N"),
        Token(TokenTypes.TEXT, "o"),
        Token(TokenTypes.TEXT, "r"),
        Token(TokenTypes.TEXT, "m"),
        Token(TokenTypes.TEXT, "a"),
        Token(TokenTypes.TEXT, "l"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "x"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.TEXT, "_"),
        Token(TokenTypes.TEXT, "o"),
        Token(TokenTypes.TEXT, "t"),
        Token(TokenTypes.TEXT, "h"),
        Token(TokenTypes.TEXT, "e"),
        Token(TokenTypes.TEXT, "r"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.TEXT, "_"),
        Token(TokenTypes.EOL),
    ]
