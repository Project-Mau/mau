from mau.lexers.text_lexer import TextLexer
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_collect_macro_arguments_single_argument():
    source = "(value1)"

    parser = init_parser(source)

    assert parser._collect_macro_args() == "value1"


def test_collect_macro_arguments_multiple_arguments():
    source = "(value1,value2)"

    parser = init_parser(source)

    assert parser._collect_macro_args() == "value1,value2"


def test_collect_macro_arguments_single_argument_with_quotes():
    source = '("value1")'

    parser = init_parser(source)

    assert parser._collect_macro_args() == '"value1"'


def test_collect_macro_arguments_single_argument_with_quotes_and_parenthesis():
    source = '("value1()")'

    parser = init_parser(source)

    assert parser._collect_macro_args() == '"value1()"'


def test_collect_macro_arguments_single_argument_with_parenthesis():
    source = "(value1())"

    parser = init_parser(source)

    assert parser._collect_macro_args() == "value1("


def test_collect_macro_arguments_multiple_argument_with_quotes_and_parenthesis():
    source = '("value1()",value2,value3)'

    parser = init_parser(source)

    assert parser._collect_macro_args() == '"value1()",value2,value3'


def test_collect_macro_arguments_multiple_argument_with_escaped_quotes():
    source = r"(\"value2,value3)"

    parser = init_parser(source)

    assert parser._collect_macro_args() == r"\"value2,value3"
