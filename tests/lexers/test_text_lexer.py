from mau.lexers.base_lexer import TokenTypes
from mau.lexers.text_lexer import TextLexer
from mau.text_buffer.text_buffer import TextBuffer
from mau.tokens.tokens import Token


def test_normal_text():
    text_buffer = TextBuffer("Normal text")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "Normal"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "text"),
        Token(TokenTypes.EOL),
    ]


def test_underscore():
    text_buffer = TextBuffer("_underscore_")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "_"),
        Token(TokenTypes.TEXT, "underscore"),
        Token(TokenTypes.LITERAL, "_"),
        Token(TokenTypes.EOL),
    ]


def test_star():
    text_buffer = TextBuffer("*star*")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "*"),
        Token(TokenTypes.TEXT, "star"),
        Token(TokenTypes.LITERAL, "*"),
        Token(TokenTypes.EOL),
    ]


def test_caret():
    text_buffer = TextBuffer("^caret^")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "^"),
        Token(TokenTypes.TEXT, "caret"),
        Token(TokenTypes.LITERAL, "^"),
        Token(TokenTypes.EOL),
    ]


def test_tilde():
    text_buffer = TextBuffer("~tilde~")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "~"),
        Token(TokenTypes.TEXT, "tilde"),
        Token(TokenTypes.LITERAL, "~"),
        Token(TokenTypes.EOL),
    ]


def test_backtick():
    text_buffer = TextBuffer("`backtick`")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "`"),
        Token(TokenTypes.TEXT, "backtick"),
        Token(TokenTypes.LITERAL, "`"),
        Token(TokenTypes.EOL),
    ]


def test_curly_braces():
    text_buffer = TextBuffer("{curly}")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "{"),
        Token(TokenTypes.TEXT, "curly"),
        Token(TokenTypes.LITERAL, "}"),
        Token(TokenTypes.EOL),
    ]


def test_round_brackets():
    text_buffer = TextBuffer("(round)")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "("),
        Token(TokenTypes.TEXT, "round"),
        Token(TokenTypes.LITERAL, ")"),
        Token(TokenTypes.EOL),
    ]


def test_square_brackets():
    text_buffer = TextBuffer("[square]")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "["),
        Token(TokenTypes.TEXT, "square"),
        Token(TokenTypes.LITERAL, "]"),
        Token(TokenTypes.EOL),
    ]


def test_macro():
    text_buffer = TextBuffer("[macro](value1,value2)")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "["),
        Token(TokenTypes.TEXT, "macro"),
        Token(TokenTypes.LITERAL, "]"),
        Token(TokenTypes.LITERAL, "("),
        Token(TokenTypes.TEXT, "value1,value2"),
        Token(TokenTypes.LITERAL, ")"),
        Token(TokenTypes.EOL),
    ]


def test_macro_named_attributes():
    text_buffer = TextBuffer("[macro](attr1=value1,attr2=value2)")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "["),
        Token(TokenTypes.TEXT, "macro"),
        Token(TokenTypes.LITERAL, "]"),
        Token(TokenTypes.LITERAL, "("),
        Token(TokenTypes.TEXT, "attr1=value1,attr2=value2"),
        Token(TokenTypes.LITERAL, ")"),
        Token(TokenTypes.EOL),
    ]


def test_escaped_underscore():
    text_buffer = TextBuffer(r"\_underscore\_")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "_"),
        Token(TokenTypes.TEXT, "underscore"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "_"),
        Token(TokenTypes.EOL),
    ]


def test_escaped_square_brackets():
    text_buffer = TextBuffer(r"\[square\]")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "["),
        Token(TokenTypes.TEXT, "square"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "]"),
        Token(TokenTypes.EOL),
    ]


def test_escaped_round_brackets():
    text_buffer = TextBuffer(r"\(round\)")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "("),
        Token(TokenTypes.TEXT, "round"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, ")"),
        Token(TokenTypes.EOL),
    ]


def test_escaped_curly_braces():
    text_buffer = TextBuffer(r"\{curly\}")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "{"),
        Token(TokenTypes.TEXT, "curly"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "}"),
        Token(TokenTypes.EOL),
    ]


def test_escaped_quotes():
    text_buffer = TextBuffer(r"\"quotes\"")
    lex = TextLexer(text_buffer)
    lex.process()

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, '"'),
        Token(TokenTypes.TEXT, "quotes"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, '"'),
        Token(TokenTypes.EOL),
    ]
