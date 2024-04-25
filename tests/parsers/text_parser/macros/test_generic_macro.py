from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import TextNode
from mau.nodes.macros import MacroNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_macro():
    source = "[macroname](value1,value2)"

    expected = [
        MacroNode(
            "macroname",
            args=["value1", "value2"],
        ),
    ]

    assert runner(source).nodes == expected


def test_incomplete_macro():
    source = "[macroname](value1"

    expected = [
        TextNode(
            "[macroname](value1",
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_arguments_with_quotes():
    source = '[macroname]("value1,value2")'

    expected = [
        MacroNode(
            "macroname",
            args=["value1,value2"],
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_named_arguments():
    source = "[macroname](name,arg1=value1)"

    expected = [
        MacroNode(
            "macroname",
            args=["name"],
            kwargs={"arg1": "value1"},
        ),
    ]

    assert runner(source).nodes == expected
