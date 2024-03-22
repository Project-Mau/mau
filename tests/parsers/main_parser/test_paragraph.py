import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.footnotes import FootnotesNode
from mau.nodes.inline import SentenceNode, StyleNode, TextNode
from mau.nodes.macros import MacroLinkNode
from mau.nodes.page import (
    ContainerNode,
    DocumentNode,
    HorizontalRuleNode,
    ParagraphNode,
)
from mau.nodes.toc import TocNode
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
            SentenceNode(
                [
                    TextNode(
                        "This is a paragraph. This is part of the same paragraph."
                    ),
                ]
            ),
            args=[],
            kwargs={},
        ),
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This is a new paragraph."),
                ]
            ),
            args=[],
            kwargs={},
        ),
    ]


def test_parse_paragraph_starting_with_a_macro():
    source = "[link](http://some.where,This) is the link I want"

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    MacroLinkNode(target="http://some.where", text="This"),
                    TextNode(" is the link I want"),
                ]
            )
        )
    ]


def test_attributes_paragraph():
    source = """
    [*type, arg1,key1=value1]
    This is text
    """

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [TextNode("This is text")],
            ),
            args=["arg1"],
            kwargs={"key1": "value1"},
            subtype="type",
        ),
    ]
