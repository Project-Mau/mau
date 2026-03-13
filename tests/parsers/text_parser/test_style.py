from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import StyleNode, TextNode
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


def test_underscore():
    source = "_Some text_"

    expected = [
        StyleNode(
            "underscore",
            content=[
                TextNode(
                    "Some text",
                    info=NodeInfo(context=generate_context(0, 1, 0, 10)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 11)),
        )
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_star():
    source = "*Some text*"

    expected = [
        StyleNode(
            "star",
            content=[
                TextNode(
                    "Some text",
                    info=NodeInfo(context=generate_context(0, 1, 0, 10)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 11)),
        )
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_caret():
    source = "^Some text^"

    expected = [
        StyleNode(
            "caret",
            content=[
                TextNode(
                    "Some text",
                    info=NodeInfo(context=generate_context(0, 1, 0, 10)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 11)),
        )
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_tilde():
    source = "~Some text~"

    expected = [
        StyleNode(
            "tilde",
            content=[
                TextNode(
                    "Some text",
                    info=NodeInfo(context=generate_context(0, 1, 0, 10)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 11)),
        )
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_style_within_style():
    source = "_*Words with two styles*_"

    expected = [
        StyleNode(
            "underscore",
            content=[
                StyleNode(
                    "star",
                    content=[
                        TextNode(
                            "Words with two styles",
                            info=NodeInfo(context=generate_context(0, 2, 0, 23)),
                        )
                    ],
                    info=NodeInfo(context=generate_context(0, 1, 0, 24)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 0, 0, 25)),
        )
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_double_style_cancels_itself():
    source = "__Text__"

    expected = [
        StyleNode(
            "underscore",
            info=NodeInfo(context=generate_context(0, 0, 0, 2)),
        ),
        TextNode(
            "Text",
            info=NodeInfo(context=generate_context(0, 2, 0, 6)),
        ),
        StyleNode(
            "underscore",
            info=NodeInfo(context=generate_context(0, 6, 0, 8)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_mix_text_and_styles():
    source = "Some text _and style_ and *more style* here"

    expected = [
        TextNode(
            "Some text ",
            info=NodeInfo(context=generate_context(0, 0, 0, 10)),
        ),
        StyleNode(
            "underscore",
            content=[
                TextNode(
                    "and style",
                    info=NodeInfo(context=generate_context(0, 11, 0, 20)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 10, 0, 21)),
        ),
        TextNode(
            " and ",
            info=NodeInfo(context=generate_context(0, 21, 0, 26)),
        ),
        StyleNode(
            "star",
            content=[
                TextNode(
                    "more style",
                    info=NodeInfo(context=generate_context(0, 27, 0, 37)),
                )
            ],
            info=NodeInfo(context=generate_context(0, 26, 0, 38)),
        ),
        TextNode(
            " here",
            info=NodeInfo(context=generate_context(0, 38, 0, 43)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)


def test_unclosed_style():
    source = "_Text"

    expected = [
        TextNode(
            "_Text",
            info=NodeInfo(context=generate_context(0, 0, 0, 5)),
        ),
    ]

    compare_nodes_sequence(runner(source).nodes, expected)
