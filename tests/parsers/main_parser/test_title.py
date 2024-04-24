from unittest.mock import patch

import pytest
from mau.text_buffer.context import Context
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.content import ContentNode
from mau.nodes.header import HeaderNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_parse_title():
    source = """
    .Just a title
    """

    parser = runner(source)

    assert parser.title == (
        "Just a title",
        Context(1, 0, "main", ".Just a title"),
        Environment(),
    )


def test_block_uses_title():
    source = """
    .Just a title
    ----
    ----
    """

    parser = runner(source)

    assert parser.nodes == [
        BlockNode(
            subtype=None,
            classes=[],
            title=SentenceNode(
                children=[
                    TextNode("Just a title"),
                ]
            ),
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]

    assert parser.title == (None, None, None)


def test_include_content_uses_title():
    source = """
    .Just a title
    << type:uri1
    """

    parser = runner(source)

    assert parser.nodes == [
        ContentNode(
            content_type="type",
            uris=["uri1"],
            title=SentenceNode(
                children=[
                    TextNode("Just a title"),
                ]
            ),
        )
    ]

    assert parser.title == (None, None, None)
