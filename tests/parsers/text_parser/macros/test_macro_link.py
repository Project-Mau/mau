import pytest

from mau.lexers.text_lexer import TextLexer
from mau.message import MauException, MauMessageType
from mau.nodes.inline import StyleNode, TextNode
from mau.nodes.macro import MacroLinkNode
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


def test_macro_link():
    source = '[link](https://somedomain.org/the/path, "link text")'

    expected = [
        MacroLinkNode(
            "https://somedomain.org/the/path",
            content=[
                TextNode(
                    "link text",
                    info=NodeInfo(context=generate_context(0, 41, 0, 50)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 52)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_link_without_text():
    source = '[link]("https://somedomain.org/the/path")'

    expected = [
        MacroLinkNode(
            "https://somedomain.org/the/path",
            content=[
                TextNode(
                    "https://somedomain.org/the/path",
                    info=NodeInfo(context=generate_context(0, 8, 0, 39)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 41)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_link_without_target():
    source = "[link]()"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Missing mandatory TARGET. Syntax: [link](TARGET, text)."
    )
    assert exc.value.message.context == generate_context(0, 0, 0, 8)


def test_macro_link_with_rich_text():
    source = (
        '[link]("https://somedomain.org/the/path", "Some text with _styled words_")'
    )

    expected = [
        MacroLinkNode(
            "https://somedomain.org/the/path",
            content=[
                TextNode(
                    "Some text with ",
                    info=NodeInfo(context=generate_context(0, 43, 0, 58)),
                ),
                StyleNode(
                    "underscore",
                    content=[
                        TextNode(
                            "styled words",
                            info=NodeInfo(context=generate_context(0, 59, 0, 71)),
                        ),
                    ],
                    info=NodeInfo(context=generate_context(0, 58, 0, 72)),
                ),
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 74)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_mailto():
    source = "[mailto](info@projectmau.org)"

    expected = [
        MacroLinkNode(
            "mailto:info@projectmau.org",
            content=[
                TextNode(
                    "info@projectmau.org",
                    info=NodeInfo(context=generate_context(0, 9, 0, 28)),
                ),
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 29)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_mailto_custom_text():
    source = '[mailto](info@projectmau.org, "my email")'

    expected = [
        MacroLinkNode(
            "mailto:info@projectmau.org",
            content=[
                TextNode(
                    "my email",
                    info=NodeInfo(context=generate_context(0, 31, 0, 39)),
                ),
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 41)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_mailto_without_target():
    source = "[mailto]()"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Missing mandatory EMAIL. Syntax: [mailto](EMAIL, text)."
    )
    assert exc.value.message.context == generate_context(0, 0, 0, 10)
