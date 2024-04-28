from unittest.mock import patch

import pytest
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.header import HeaderNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.toc import TocEntryNode, TocNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


@patch("mau.parsers.main_parser.header_anchor")
def test_engine_mau(mock_header_anchor):
    mock_header_anchor.return_value = "XXYY"

    source = """
    = Header 1

    = Header 2

    [*sometype, engine=mau]
    ----
    = Header 3

    = Header 4
    ----
    """

    par = runner(source)

    assert par.nodes == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 1")]),
            level="1",
            anchor="XXYY",
        ),
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 2")]),
            level="1",
            anchor="XXYY",
        ),
        BlockNode(
            subtype="sometype",
            children=[
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Header 3")]),
                    level="1",
                    anchor="XXYY",
                ),
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Header 4")]),
                    level="1",
                    anchor="XXYY",
                ),
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine="mau",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
    ]

    assert par.toc_manager.headers == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 1")]),
            level="1",
            anchor="XXYY",
        ),
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 2")]),
            level="1",
            anchor="XXYY",
        ),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_engine_mau_multiple_blocks_are_independent(mock_header_anchor):
    mock_header_anchor.return_value = "XXYY"

    source = """
    = Header 1

    = Header 2

    [*sometype, engine=mau]
    ----
    = Header 3

    = Header 4
    ----

    [*sometype, engine=mau]
    ----
    = Header 5

    = Header 6
    ----
    """

    par = runner(source)

    assert par.nodes == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 1")]),
            level="1",
            anchor="XXYY",
        ),
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 2")]),
            level="1",
            anchor="XXYY",
        ),
        BlockNode(
            subtype="sometype",
            children=[
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Header 3")]),
                    level="1",
                    anchor="XXYY",
                ),
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Header 4")]),
                    level="1",
                    anchor="XXYY",
                ),
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine="mau",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
        BlockNode(
            subtype="sometype",
            children=[
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Header 5")]),
                    level="1",
                    anchor="XXYY",
                ),
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Header 6")]),
                    level="1",
                    anchor="XXYY",
                ),
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine="mau",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
    ]

    assert par.toc_manager.headers == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 1")]),
            level="1",
            anchor="XXYY",
        ),
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 2")]),
            level="1",
            anchor="XXYY",
        ),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_engine_mau_toc(mock_header_anchor):
    mock_header_anchor.return_value = "XXYY"

    source = """
    = Header 1

    = Header 2

    [*sometype, engine=mau]
    ----
    = Header 3

    = Header 4

    ::toc:
    ----

    ::toc:
    """

    par = runner(source)

    assert par.nodes == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 1")]),
            level="1",
            anchor="XXYY",
        ),
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 2")]),
            level="1",
            anchor="XXYY",
        ),
        BlockNode(
            subtype="sometype",
            children=[
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Header 3")]),
                    level="1",
                    anchor="XXYY",
                ),
                HeaderNode(
                    value=SentenceNode(children=[TextNode("Header 4")]),
                    level="1",
                    anchor="XXYY",
                ),
                TocNode(
                    children=[
                        TocEntryNode(
                            value=SentenceNode(children=[TextNode("Header 3")]),
                            anchor="XXYY",
                        ),
                        TocEntryNode(
                            value=SentenceNode(children=[TextNode("Header 4")]),
                            anchor="XXYY",
                        ),
                    ]
                ),
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine="mau",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
        TocNode(
            children=[
                TocEntryNode(
                    value=SentenceNode(children=[TextNode("Header 1")]), anchor="XXYY"
                ),
                TocEntryNode(
                    value=SentenceNode(children=[TextNode("Header 2")]), anchor="XXYY"
                ),
            ]
        ),
    ]

    assert par.toc_manager.headers == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 1")]),
            level="1",
            anchor="XXYY",
        ),
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header 2")]),
            level="1",
            anchor="XXYY",
        ),
    ]


def test_block_mau_has_no_external_variables():
    source = """
    :answer:42
    [*block, engine=mau]
    ----
    The answer is {answer}.
    ----
    """

    with pytest.raises(MauErrorException):
        assert runner(source)
