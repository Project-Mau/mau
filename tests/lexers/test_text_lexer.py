from mau.lexers.base_lexer import TokenTypes
from mau.lexers.text_lexer import TextLexer
from mau.tokens.tokens import Token

from tests.helpers import init_lexer_factory, lexer_runner_factory

init_lexer = init_lexer_factory(TextLexer)

runner = lexer_runner_factory(TextLexer)


def test_normal_text():
    lex = runner("Normal text")

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "Normal"),
        Token(TokenTypes.TEXT, " "),
        Token(TokenTypes.TEXT, "text"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_underscore():
    lex = runner("_underscore_")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "_"),
        Token(TokenTypes.TEXT, "underscore"),
        Token(TokenTypes.LITERAL, "_"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_star():
    lex = runner("*star*")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "*"),
        Token(TokenTypes.TEXT, "star"),
        Token(TokenTypes.LITERAL, "*"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_caret():
    lex = runner("^caret^")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "^"),
        Token(TokenTypes.TEXT, "caret"),
        Token(TokenTypes.LITERAL, "^"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_tilde():
    lex = runner("~tilde~")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "~"),
        Token(TokenTypes.TEXT, "tilde"),
        Token(TokenTypes.LITERAL, "~"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_backtick():
    lex = runner("`backtick`")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "`"),
        Token(TokenTypes.TEXT, "backtick"),
        Token(TokenTypes.LITERAL, "`"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_dollar():
    lex = runner("$dollar$")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "$"),
        Token(TokenTypes.TEXT, "dollar"),
        Token(TokenTypes.LITERAL, "$"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_percent():
    lex = runner("%percent%")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "%"),
        Token(TokenTypes.TEXT, "percent"),
        Token(TokenTypes.LITERAL, "%"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_curly_braces():
    lex = runner("{curly}")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "{"),
        Token(TokenTypes.TEXT, "curly"),
        Token(TokenTypes.LITERAL, "}"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_round_brackets():
    lex = runner("(round)")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "("),
        Token(TokenTypes.TEXT, "round"),
        Token(TokenTypes.LITERAL, ")"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_square_brackets():
    lex = runner("[square]")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "["),
        Token(TokenTypes.TEXT, "square"),
        Token(TokenTypes.LITERAL, "]"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_macro():
    lex = runner("[macro](value1,value2)")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "["),
        Token(TokenTypes.TEXT, "macro"),
        Token(TokenTypes.LITERAL, "]"),
        Token(TokenTypes.LITERAL, "("),
        Token(TokenTypes.TEXT, "value1,value2"),
        Token(TokenTypes.LITERAL, ")"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_macro_named_attributes():
    lex = runner("[macro](attr1=value1,attr2=value2)")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "["),
        Token(TokenTypes.TEXT, "macro"),
        Token(TokenTypes.LITERAL, "]"),
        Token(TokenTypes.LITERAL, "("),
        Token(TokenTypes.TEXT, "attr1=value1,attr2=value2"),
        Token(TokenTypes.LITERAL, ")"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_underscore():
    lex = runner(r"\_underscore\_")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "_"),
        Token(TokenTypes.TEXT, "underscore"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "_"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_square_brackets():
    lex = runner(r"\[square\]")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "["),
        Token(TokenTypes.TEXT, "square"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "]"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_round_brackets():
    lex = runner(r"\(round\)")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "("),
        Token(TokenTypes.TEXT, "round"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, ")"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_curly_braces():
    lex = runner(r"\{curly\}")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "{"),
        Token(TokenTypes.TEXT, "curly"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "}"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_quotes():
    lex = runner(r"\"quotes\"")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, '"'),
        Token(TokenTypes.TEXT, "quotes"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, '"'),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_backticks():
    lex = runner(r"\`backticks\`")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "`"),
        Token(TokenTypes.TEXT, "backticks"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "`"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_dollar():
    lex = runner(r"\$dollar\$")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "$"),
        Token(TokenTypes.TEXT, "dollar"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "$"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_escaped_percent():
    lex = runner(r"\%pecent\%")

    assert lex.tokens == [
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "%"),
        Token(TokenTypes.TEXT, "pecent"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "%"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]
