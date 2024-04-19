from unittest.mock import patch

import pytest
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.header import HeaderNode
from mau.nodes.inline import TextNode
from mau.nodes.toc import TocEntryNode, TocNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_engine_mau():
    source = """
    [*sometype1, engine=group, group=somegroup, position=left]
    ----
    Block 1
    ----
    
    [*sometype2, engine=group, group=somegroup, position=right]
    ----
    Block 2
    ----
    """

    par = runner(source)

    assert par.nodes == []

    assert par.grouped_blocks == {
        "somegroup": {
            "left": BlockNode(
                subtype="sometype1",
                children=[
                    ParagraphNode(
                        children=[
                            TextNode("Block 1"),
                        ]
                    ),
                ],
                secondary_children=[],
                classes=[],
                title=None,
                engine="group",
                preprocessor="none",
                args=[],
                kwargs={},
            ),
            "right": BlockNode(
                subtype="sometype2",
                children=[
                    ParagraphNode(
                        children=[
                            TextNode("Block 2"),
                        ]
                    ),
                ],
                secondary_children=[],
                classes=[],
                title=None,
                engine="group",
                preprocessor="none",
                args=[],
                kwargs={},
            ),
        }
    }

    # assert par.toc_manager.headers == [
    #     HeaderNode(value=[TextNode("Header 1")], level="1", anchor="XXYY"),
    #     HeaderNode(value=[TextNode("Header 2")], level="1", anchor="XXYY"),
    # ]
