# import textwrap
# from unittest.mock import patch

from mau.lexers.main_lexer import MainLexer

from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import ContainerNode, HeaderNode, ParagraphNode
from mau.nodes.toc import CommandTocNode, TocEntryNode
from mau.parsers.main_parser import MainParser
from mau.environment.environment import Environment

# from mau.parsers.references import reference_anchor

from tests.helpers import init_parser_factory, parser_runner_factory

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
        "toc": CommandTocNode(entries=[]),
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
            SentenceNode(
                [
                    TextNode("This is a paragraph."),
                ]
            )
        ),
        ParagraphNode(
            content=SentenceNode(
                [
                    TextNode("This is an important paragraph."),
                ]
            ),
            tags=["important"],
        ),
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This is another paragraph."),
                ]
            )
        ),
        ParagraphNode(
            content=SentenceNode(
                [
                    TextNode("This is another important paragraph."),
                ]
            ),
            tags=["important"],
        ),
    ]

    assert parser.output == {
        "content": ContainerNode(content=nodes),
        "footnotes": [],
        "references": {},
        "toc": CommandTocNode(entries=[]),
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
            SentenceNode(
                [
                    TextNode("This is a paragraph."),
                ]
            )
        ),
        ParagraphNode(
            content=SentenceNode(
                [
                    TextNode("This is an important paragraph."),
                ]
            ),
            tags=["important"],
        ),
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This is another paragraph."),
                ]
            )
        ),
        ParagraphNode(
            content=SentenceNode(
                [
                    TextNode("This is another important paragraph."),
                ]
            ),
            tags=["important"],
        ),
    ]

    important_nodes = [
        ParagraphNode(
            content=SentenceNode(
                [
                    TextNode("This is an important paragraph."),
                ]
            ),
            tags=["important"],
        ),
        ParagraphNode(
            content=SentenceNode(
                [
                    TextNode("This is another important paragraph."),
                ]
            ),
            tags=["important"],
        ),
    ]

    assert parser.output == {
        "content": ContainerNode(content=nodes),
        "footnotes": [],
        "references": {},
        "toc": CommandTocNode(entries=[]),
        "custom_filters": {"important_nodes": important_nodes},
    }