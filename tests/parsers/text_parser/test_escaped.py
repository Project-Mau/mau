from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import TextNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_dollar():
    source = "$Many different words$"

    expected = [
        TextNode("Many different words"),
    ]

    assert runner(source).nodes == expected


def test_percent():
    source = "%Many different words%"

    expected = [
        TextNode("Many different words"),
    ]

    assert runner(source).nodes == expected


def test_dollar_can_escape_percent():
    source = "$Many %different% words$"

    expected = [
        TextNode("Many %different% words"),
    ]

    assert runner(source).nodes == expected


def test_dollar_can_escape_backtick():
    source = "$Many `different` words$"

    expected = [
        TextNode("Many `different` words"),
    ]

    assert runner(source).nodes == expected


def test_percent_can_escape_dollar():
    source = "%Many $different$ words%"

    expected = [
        TextNode("Many $different$ words"),
    ]

    assert runner(source).nodes == expected


def test_percent_can_escape_backtick():
    source = "%Many `different` words%"

    expected = [
        TextNode("Many `different` words"),
    ]

    assert runner(source).nodes == expected


def test_dollar_escapes_style():
    source = "$Many _different_ words$"

    expected = [
        TextNode("Many _different_ words"),
    ]

    assert runner(source).nodes == expected


def test_percent_escapes_style():
    source = "%Many _different_ words%"

    expected = [
        TextNode("Many _different_ words"),
    ]

    assert runner(source).nodes == expected


def test_escaped_dollar():
    source = r"$\$$"

    expected = [
        TextNode("$"),
    ]

    assert runner(source).nodes == expected


def test_escaped_percent():
    source = r"%\%%"

    expected = [
        TextNode("%"),
    ]

    assert runner(source).nodes == expected


def test_open_dollar():
    source = r"$Many different words"

    expected = [
        TextNode("$Many different words"),
    ]

    assert runner(source).nodes == expected


def test_open_percent():
    source = r"%Many different words"

    expected = [
        TextNode("%Many different words"),
    ]

    assert runner(source).nodes == expected
