import pytest

from mau.lexers.text_lexer import TextLexer
from mau.message import MauException, MauMessageType
from mau.nodes.macro import MacroRawNode
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


def test_macro_raw():
    source = "[raw](somevalue)"

    expected = [
        MacroRawNode(
            "somevalue",
            info=NodeInfo(context=generate_context(0, 0, 0, 16)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)


def test_macro_raw_without_value():
    source = "[raw]()"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Missing mandatory VALUE. Syntax: [raw](VALUE)."
    assert exc.value.message.context == generate_context(0, 0, 0, 7)
