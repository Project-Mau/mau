# import textwrap
# from unittest.mock import patch

from mau.environment.environment import Environment
from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import TextNode
from mau.nodes.page import ContainerNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.toc import TocNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

# from mau.parsers.references import reference_anchor


init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_custom_filters_is_empty_by_default():
    source = """
    """

    parser = runner(source)

    assert parser.output == {
        "content": ContainerNode([]),
        "footnotes": [],
        "references": {},
        "toc": TocNode(),
        "custom_filters": {},
    }


def test_custom_filter_no_filter():
    source = """
    This is a paragraph.

    [#important]
    This is an important paragraph.
    
    This is another paragraph.
    
    [#important]
    This is another important paragraph.
    """

    def all_nodes(nodes):
        return nodes

    environment = Environment()
    environment.setvar("mau.parser.custom_filters", {"all_nodes": all_nodes})

    parser = runner(source, environment)

    nodes = [
        ParagraphNode(
            children=[
                TextNode("This is a paragraph."),
            ]
        ),
        ParagraphNode(
            children=[
                TextNode("This is an important paragraph."),
            ],
            tags=["important"],
        ),
        ParagraphNode(
            children=[
                TextNode("This is another paragraph."),
            ]
        ),
        ParagraphNode(
            children=[
                TextNode("This is another important paragraph."),
            ],
            tags=["important"],
        ),
    ]

    assert parser.output == {
        "content": ContainerNode(children=nodes),
        "footnotes": [],
        "references": {},
        "toc": TocNode(),
        "custom_filters": {"all_nodes": nodes},
    }


def test_custom_filter_extract_tags():
    source = """
    This is a paragraph.

    [#important]
    This is an important paragraph.
    
    This is another paragraph.
    
    [#important]
    This is another important paragraph.
    """

    def important_nodes(nodes):
        return [n for n in nodes if "important" in n.tags]

    environment = Environment()
    environment.setvar(
        "mau.parser.custom_filters", {"important_nodes": important_nodes}
    )

    parser = runner(source, environment)

    nodes = [
        ParagraphNode(
            children=[
                TextNode("This is a paragraph."),
            ]
        ),
        ParagraphNode(
            children=[
                TextNode("This is an important paragraph."),
            ],
            tags=["important"],
        ),
        ParagraphNode(
            children=[
                TextNode("This is another paragraph."),
            ]
        ),
        ParagraphNode(
            children=[
                TextNode("This is another important paragraph."),
            ],
            tags=["important"],
        ),
    ]

    important_nodes = [
        ParagraphNode(
            children=[
                TextNode("This is an important paragraph."),
            ],
            tags=["important"],
        ),
        ParagraphNode(
            children=[
                TextNode("This is another important paragraph."),
            ],
            tags=["important"],
        ),
    ]

    assert parser.output == {
        "content": ContainerNode(children=nodes),
        "footnotes": [],
        "references": {},
        "toc": TocNode(),
        "custom_filters": {"important_nodes": important_nodes},
    }
