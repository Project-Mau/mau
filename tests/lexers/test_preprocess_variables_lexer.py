from mau.lexers.base_lexer import TokenTypes
from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer
from mau.tokens.tokens import Token

from tests.helpers import init_lexer_factory, lexer_runner_factory

init_lexer = init_lexer_factory(PreprocessVariablesLexer)

runner = lexer_runner_factory(PreprocessVariablesLexer)


def test_normal_text():
    lex = runner("Some text")

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
        Token(TokenTypes.EOF),
    ]


def test_match_only_backticks_and_curly_braces():
    lex = runner("Normal text `{curly}` _other_ *text*")

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
        Token(TokenTypes.EOF),
    ]


def test_escape_curly_braces():
    lex = runner(r"Normal text \{curly\} _other_ *text*")

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
        Token(TokenTypes.EOF),
    ]


def test_preserve_escapes():
    lex = runner(r"Normal \text \_other\_")

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
        Token(TokenTypes.EOF),
    ]
