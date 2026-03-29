from mau.environment.environment import Environment
from mau.lexers.text_lexer import TextLexer
from mau.parsers.text_parser import TextParser
from mau.test_helpers import (
    compare_asdict_object,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)
from mau.token import Token, TokenType

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_collect_macro_arguments_single_argument():
    source = "value1)"

    parser = init_parser(source, Environment())

    compare_asdict_object(
        parser._collect_macro_args(),
        Token(TokenType.TEXT, "value1", generate_context(0, 0, 0, 6)),
    )


def test_collect_macro_arguments_multiple_arguments():
    source = "value1,value2)"

    parser = init_parser(source, Environment())

    compare_asdict_object(
        parser._collect_macro_args(),
        Token(TokenType.TEXT, "value1,value2", generate_context(0, 0, 0, 13)),
    )


def test_collect_macro_arguments_single_argument_with_quotes():
    source = '"value1")'

    parser = init_parser(source, Environment())

    compare_asdict_object(
        parser._collect_macro_args(),
        Token(TokenType.TEXT, '"value1"', generate_context(0, 0, 0, 8)),
    )


def test_collect_macro_arguments_single_argument_with_quotes_and_parenthesis():
    source = '"value1()")'

    parser = init_parser(source, Environment())

    compare_asdict_object(
        parser._collect_macro_args(),
        Token(TokenType.TEXT, '"value1()"', generate_context(0, 0, 0, 10)),
    )


def test_collect_macro_arguments_single_argument_with_parenthesis():
    source = "value1())"

    parser = init_parser(source, Environment())

    compare_asdict_object(
        parser._collect_macro_args(),
        Token(TokenType.TEXT, "value1(", generate_context(0, 0, 0, 7)),
    )


def test_collect_macro_arguments_multiple_argument_with_quotes_and_parenthesis():
    source = '"value1()",value2,value3)'

    parser = init_parser(source, Environment())

    compare_asdict_object(
        parser._collect_macro_args(),
        Token(
            TokenType.TEXT, '"value1()",value2,value3', generate_context(0, 0, 0, 24)
        ),
    )


def test_collect_macro_arguments_multiple_argument_with_escaped_quotes():
    source = r"\"value2,value3)"

    parser = init_parser(source, Environment())

    compare_asdict_object(
        parser._collect_macro_args(),
        Token(TokenType.TEXT, r"\"value2,value3", generate_context(0, 0, 0, 15)),
    )
