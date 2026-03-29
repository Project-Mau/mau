import pytest

from mau.lexers.text_lexer import TextLexer
from mau.message import MauException, MauMessageType
from mau.nodes.inline import TextNode
from mau.nodes.macro import MacroHeaderNode
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


def test_macro_header():
    source = '[header](id, "link text")'

    expected = [
        MacroHeaderNode(
            "id",
            content=[
                TextNode(
                    "link text",
                    info=NodeInfo(context=generate_context(0, 14, 0, 23)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 25)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)
    compare_nodes_sequence(parser.header_links, expected)


def test_macro_header_without_text():
    source = "[header](id)"

    expected = [
        MacroHeaderNode(
            "id",
            content=[],
            info=NodeInfo(context=generate_context(0, 0, 0, 12)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)
    compare_nodes_sequence(parser.header_links, expected)


def test_macro_header_without_target():
    source = "[header]()"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Missing mandatory ID. Syntax: [header](ID, TEXT)."
    assert exc.value.message.context == generate_context(0, 0, 0, 10)
