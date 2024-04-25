from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import StyleNode, TextNode
from mau.nodes.macros import MacroLinkNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_macro_link():
    source = '[link](https://somedomain.org/the/path, "link text")'

    expected = [
        MacroLinkNode(
            "https://somedomain.org/the/path", children=[TextNode("link text")]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_link_without_text():
    source = '[link]("https://somedomain.org/the/path")'

    expected = [
        MacroLinkNode(
            "https://somedomain.org/the/path",
            children=[TextNode("https://somedomain.org/the/path")],
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_link_with_rich_text():
    source = (
        '[link]("https://somedomain.org/the/path", "Some text with _styled words_")'
    )

    expected = [
        MacroLinkNode(
            "https://somedomain.org/the/path",
            children=[
                TextNode("Some text with "),
                StyleNode(value="underscore", children=[TextNode("styled words")]),
            ],
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_mailto():
    source = "[mailto](info@projectmau.org)"

    expected = [
        MacroLinkNode(
            "mailto:info@projectmau.org", children=[TextNode("info@projectmau.org")]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_mailto_custom_text():
    source = '[mailto](info@projectmau.org, "my email")'

    expected = [
        MacroLinkNode("mailto:info@projectmau.org", children=[TextNode("my email")]),
    ]

    assert runner(source).nodes == expected
