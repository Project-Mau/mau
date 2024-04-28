from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import StyleNode, TextNode, VerbatimNode
from mau.nodes.macros import MacroClassNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_single_class():
    source = 'Some text [class]("text with that class", classname)'

    expected = [
        TextNode("Some text "),
        MacroClassNode(
            classes=["classname"],
            children=[
                TextNode("text with that class"),
            ],
        ),
    ]

    assert runner(source).nodes == expected


def test_multiple_classes():
    source = 'Some text [class]("text with that class", classname1, classname2)'

    expected = [
        TextNode("Some text "),
        MacroClassNode(
            classes=["classname1", "classname2"],
            children=[
                TextNode("text with that class"),
            ],
        ),
    ]

    assert runner(source).nodes == expected


def test_parse_class_with_rich_text():
    source = '[class]("Some text with `verbatim words` and _styled ones_", classname)'

    expected = [
        MacroClassNode(
            classes=["classname"],
            children=[
                TextNode("Some text with "),
                VerbatimNode("verbatim words"),
                TextNode(" and "),
                StyleNode(value="underscore", children=[TextNode("styled ones")]),
            ],
        ),
    ]

    assert runner(source).nodes == expected
