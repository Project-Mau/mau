from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import StyleNode, TextNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_underscore():
    source = "_Some text_"

    expected = [
        StyleNode(
            value="underscore",
            children=[
                TextNode("Some text"),
            ],
        ),
    ]

    assert runner(source).nodes == expected


def test_star():
    source = "*Some text*"

    expected = [
        StyleNode(
            value="star",
            children=[
                TextNode("Some text"),
            ],
        ),
    ]

    assert runner(source).nodes == expected


def test_caret():
    source = "^Some text^"

    expected = [
        StyleNode(
            value="caret",
            children=[
                TextNode("Some text"),
            ],
        ),
    ]

    assert runner(source).nodes == expected


def test_tilde():
    source = "~Some text~"

    expected = [
        StyleNode(
            value="tilde",
            children=[
                TextNode("Some text"),
            ],
        ),
    ]

    assert runner(source).nodes == expected


def test_style_within_style():
    source = "_*Words with two styles*_"

    expected = [
        StyleNode(
            value="underscore",
            children=[
                StyleNode(
                    value="star",
                    children=[TextNode("Words with two styles")],
                )
            ],
        )
    ]

    assert runner(source).nodes == expected


def test_double_style_cancels_itself():
    source = "__Text__"

    expected = [
        StyleNode(value="underscore"),
        TextNode("Text"),
        StyleNode(value="underscore"),
    ]

    assert runner(source).nodes == expected


def test_mix_text_and_styles():
    source = "Some text _and style_ and *more style* here"

    expected = [
        TextNode("Some text "),
        StyleNode(
            value="underscore",
            children=[
                TextNode("and style"),
            ],
        ),
        TextNode(" and "),
        StyleNode(
            value="star",
            children=[
                TextNode("more style"),
            ],
        ),
        TextNode(" here"),
    ]

    assert runner(source).nodes == expected


def test_unclosed_style():
    source = "_Text"

    expected = [
        TextNode("_Text"),
    ]

    assert runner(source).nodes == expected
