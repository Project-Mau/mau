from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.macros import MacroLinkNode
from mau.nodes.paragraph import ParagraphNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_parse_paragraphs():
    source = """
    This is a paragraph.
    This is part of the same paragraph.

    This is a new paragraph.
    """

    assert runner(source).nodes == [
        ParagraphNode(
            children=[
                TextNode("This is a paragraph. This is part of the same paragraph."),
            ],
            args=[],
            kwargs={},
        ),
        ParagraphNode(
            children=[
                TextNode("This is a new paragraph."),
            ],
            args=[],
            kwargs={},
        ),
    ]


def test_parse_paragraph_starting_with_a_macro():
    source = "[link](http://some.where,This) is the link I want"

    assert runner(source).nodes == [
        ParagraphNode(
            children=[
                MacroLinkNode(target="http://some.where", children=[TextNode("This")]),
                TextNode(" is the link I want"),
            ]
        )
    ]


def test_attributes_paragraph():
    source = """
    [*type, arg1,key1=value1]
    This is text
    """

    assert runner(source).nodes == [
        ParagraphNode(
            children=[TextNode("This is text")],
            args=["arg1"],
            kwargs={"key1": "value1"},
            subtype="type",
        ),
    ]


def test_paragraph_title():
    source = """
    .Title
    This is text
    """

    parser = runner(source)

    assert parser.nodes == [
        ParagraphNode(
            children=[TextNode("This is text")],
            title=SentenceNode(children=[TextNode("Title")]),
        ),
    ]

    paragraph_node = parser.nodes[0]
    text_node = paragraph_node.title.children[0]

    assert text_node.parent == paragraph_node
    assert text_node.parent_position == "title"
