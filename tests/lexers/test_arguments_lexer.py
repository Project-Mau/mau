from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.lexers.base_lexer import TokenType
from mau.test_helpers import (
    compare_asdict_list,
    generate_context,
    init_lexer_factory,
    lexer_runner_factory,
)
from mau.token import Token

init_lexer = init_lexer_factory(ArgumentsLexer)

runner = lexer_runner_factory(ArgumentsLexer)


def test_single_unnamed_argument():
    lex = runner("value1")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "value1", generate_context(0, 0, 0, 6)),
            Token(TokenType.EOF, "", generate_context(0, 6, 0, 6)),
        ],
    )


def test_single_named_argument():
    lex = runner("argument1=value1")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "argument1", generate_context(0, 0, 0, 9)),
            Token(TokenType.LITERAL, "=", generate_context(0, 9, 0, 10)),
            Token(TokenType.TEXT, "value1", generate_context(0, 10, 0, 16)),
            Token(TokenType.EOF, "", generate_context(0, 16, 0, 16)),
        ],
    )


def test_multiple_unnamed_arguments():
    lex = runner("value1, value2")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "value1", generate_context(0, 0, 0, 6)),
            Token(TokenType.LITERAL, ",", generate_context(0, 6, 0, 7)),
            Token(TokenType.WHITESPACE, " ", generate_context(0, 7, 0, 8)),
            Token(TokenType.TEXT, "value2", generate_context(0, 8, 0, 14)),
            Token(TokenType.EOF, "", generate_context(0, 14, 0, 14)),
        ],
    )


def test_multiple_named_arguments():
    lex = runner("argument1=value1, argument2=value2")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "argument1", generate_context(0, 0, 0, 9)),
            Token(TokenType.LITERAL, "=", generate_context(0, 9, 0, 10)),
            Token(TokenType.TEXT, "value1", generate_context(0, 10, 0, 16)),
            Token(TokenType.LITERAL, ",", generate_context(0, 16, 0, 17)),
            Token(TokenType.WHITESPACE, " ", generate_context(0, 17, 0, 18)),
            Token(TokenType.TEXT, "argument2", generate_context(0, 18, 0, 27)),
            Token(TokenType.LITERAL, "=", generate_context(0, 27, 0, 28)),
            Token(TokenType.TEXT, "value2", generate_context(0, 28, 0, 34)),
            Token(TokenType.EOF, "", generate_context(0, 34, 0, 34)),
        ],
    )


def test_mixed_arguments():
    lex = runner("value1, value2,argument1=value1, argument2=value2")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "value1", generate_context(0, 0, 0, 6)),
            Token(TokenType.LITERAL, ",", generate_context(0, 6, 0, 7)),
            Token(TokenType.WHITESPACE, " ", generate_context(0, 7, 0, 8)),
            Token(TokenType.TEXT, "value2", generate_context(0, 8, 0, 14)),
            Token(TokenType.LITERAL, ",", generate_context(0, 14, 0, 15)),
            Token(TokenType.TEXT, "argument1", generate_context(0, 15, 0, 24)),
            Token(TokenType.LITERAL, "=", generate_context(0, 24, 0, 25)),
            Token(TokenType.TEXT, "value1", generate_context(0, 25, 0, 31)),
            Token(TokenType.LITERAL, ",", generate_context(0, 31, 0, 32)),
            Token(TokenType.WHITESPACE, " ", generate_context(0, 32, 0, 33)),
            Token(TokenType.TEXT, "argument2", generate_context(0, 33, 0, 42)),
            Token(TokenType.LITERAL, "=", generate_context(0, 42, 0, 43)),
            Token(TokenType.TEXT, "value2", generate_context(0, 43, 0, 49)),
            Token(TokenType.EOF, "", generate_context(0, 49, 0, 49)),
        ],
    )


def test_quotes():
    lex = runner('argument1="value1,value2"')

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "argument1", generate_context(0, 0, 0, 9)),
            Token(TokenType.LITERAL, "=", generate_context(0, 9, 0, 10)),
            Token(TokenType.LITERAL, '"', generate_context(0, 10, 0, 11)),
            Token(TokenType.TEXT, "value1", generate_context(0, 11, 0, 17)),
            Token(TokenType.LITERAL, ",", generate_context(0, 17, 0, 18)),
            Token(TokenType.TEXT, "value2", generate_context(0, 18, 0, 24)),
            Token(TokenType.LITERAL, '"', generate_context(0, 24, 0, 25)),
            Token(TokenType.EOF, "", generate_context(0, 25, 0, 25)),
        ],
    )


def test_spaces():
    lex = runner("argument1=value1 value2")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "argument1", generate_context(0, 0, 0, 9)),
            Token(TokenType.LITERAL, "=", generate_context(0, 9, 0, 10)),
            Token(TokenType.TEXT, "value1", generate_context(0, 10, 0, 16)),
            Token(TokenType.WHITESPACE, " ", generate_context(0, 16, 0, 17)),
            Token(TokenType.TEXT, "value2", generate_context(0, 17, 0, 23)),
            Token(TokenType.EOF, "", generate_context(0, 23, 0, 23)),
        ],
    )


def test_escaped_quotes():
    lex = runner(r"argument \"with\" quotes")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "argument", generate_context(0, 0, 0, 8)),
            Token(TokenType.WHITESPACE, " ", generate_context(0, 8, 0, 9)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 9, 0, 10)),
            Token(TokenType.LITERAL, '"', generate_context(0, 10, 0, 11)),
            Token(TokenType.TEXT, "with", generate_context(0, 11, 0, 15)),
            Token(TokenType.LITERAL, "\\", generate_context(0, 15, 0, 16)),
            Token(TokenType.LITERAL, '"', generate_context(0, 16, 0, 17)),
            Token(TokenType.WHITESPACE, " ", generate_context(0, 17, 0, 18)),
            Token(TokenType.TEXT, "quotes", generate_context(0, 18, 0, 24)),
            Token(TokenType.EOF, "", generate_context(0, 24, 0, 24)),
        ],
    )
