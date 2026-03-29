from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import TextNode
from mau.nodes.node import NodeInfo
from mau.parsers.text_parser import TextParser
from mau.test_helpers import (
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_empty_text():
    source = ""

    compare_nodes_sequence(runner(source).nodes, [])


def test_parse_word():
    source = "Word"

    expected = [
        TextNode(
            "Word",
            info=NodeInfo(context=generate_context(0, 0, 0, 4)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_multiple_words():
    source = "Many different words"

    expected = [
        TextNode(
            "Many different words",
            info=NodeInfo(context=generate_context(0, 0, 0, 20)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_parse_escape_word():
    source = r"\Escaped"

    expected = [
        TextNode(
            "Escaped",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_parse_escape_symbol():
    source = r"\"Escaped"

    expected = [
        TextNode(
            '"Escaped',
            info=NodeInfo(context=generate_context(0, 0, 0, 9)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_square_brackets():
    source = "This contains [ and ] and [this]"

    expected = [
        TextNode(
            "This contains [ and ] and [this]",
            info=NodeInfo(context=generate_context(0, 0, 0, 32)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)
