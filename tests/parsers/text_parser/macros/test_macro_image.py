import pytest

from mau.lexers.text_lexer import TextLexer
from mau.message import MauException, MauMessageType
from mau.nodes.macro import MacroImageNode
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


def test_macro_image():
    source = "[image](/the/path.jpg)"

    expected = [
        MacroImageNode(
            "/the/path.jpg",
            info=NodeInfo(context=generate_context(0, 0, 0, 22)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_image_with_alt_text():
    source = '[image](/the/path.jpg, "alt name")'

    expected = [
        MacroImageNode(
            "/the/path.jpg",
            alt_text="alt name",
            info=NodeInfo(context=generate_context(0, 0, 0, 34)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_image_with_width_and_height():
    source = "[image](/the/path.jpg, width=1200, height=600)"

    expected = [
        MacroImageNode(
            "/the/path.jpg",
            alt_text=None,
            width="1200",
            height="600",
            info=NodeInfo(context=generate_context(0, 0, 0, 46)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_image_without_uri():
    source = "[image]()"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Missing mandatory URI. Syntax: [image](URI, alt_text, width, height)."
    )
    assert exc.value.message.context == generate_context(0, 0, 0, 9)
