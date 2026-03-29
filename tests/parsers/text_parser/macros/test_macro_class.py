import pytest

from mau.lexers.text_lexer import TextLexer
from mau.message import MauException, MauMessageType
from mau.nodes.inline import StyleNode, TextNode, VerbatimNode
from mau.nodes.macro import MacroClassNode
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


def test_macro_class_with_single_class():
    source = '[class]("text with that class", classname)'

    expected = [
        MacroClassNode(
            ["classname"],
            content=[
                TextNode(
                    "text with that class",
                    info=NodeInfo(context=generate_context(0, 9, 0, 29)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 42)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_class_with_multiple_classes():
    source = '[class]("text with that class", classname1, classname2)'

    expected = [
        MacroClassNode(
            ["classname1", "classname2"],
            content=[
                TextNode(
                    "text with that class",
                    info=NodeInfo(context=generate_context(0, 9, 0, 29)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 55)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_class_with_rich_text():
    source = '[class]("Some text with `verbatim words` and _styled ones_", classname)'

    expected = [
        MacroClassNode(
            ["classname"],
            content=[
                TextNode(
                    "Some text with ",
                    info=NodeInfo(context=generate_context(0, 9, 0, 24)),
                ),
                VerbatimNode(
                    "verbatim words",
                    info=NodeInfo(context=generate_context(0, 24, 0, 40)),
                ),
                TextNode(
                    " and ",
                    info=NodeInfo(context=generate_context(0, 40, 0, 45)),
                ),
                StyleNode(
                    "underscore",
                    content=[
                        TextNode(
                            "styled ones",
                            info=NodeInfo(context=generate_context(0, 46, 0, 57)),
                        )
                    ],
                    info=NodeInfo(context=generate_context(0, 45, 0, 58)),
                ),
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 71)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_class_without_classes():
    source = '[class]("text with that class")'

    expected = [
        MacroClassNode(
            [],
            content=[
                TextNode(
                    "text with that class",
                    info=NodeInfo(context=generate_context(0, 9, 0, 29)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 31)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_macro_class_without_text():
    source = "[class]()"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Missing mandatory TEXT. Syntax: [class](TEXT, class1, class2, ...)."
    )
    assert exc.value.message.context == generate_context(0, 0, 0, 9)
