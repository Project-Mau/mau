from unittest.mock import patch

from mau.lexers.main_lexer import MainLexer
from mau.nodes.page import BlockNode, CommandTocNode, HeaderNode
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

    [sometype, engine=mau]
    ----
    = Header 3

    = Header 4
    ----
    """

    par = runner(source)

    assert par.nodes == [
        HeaderNode("Header 1", "1", "XXYY"),
        HeaderNode("Header 2", "1", "XXYY"),
        BlockNode(
            blocktype="sometype",
            content=[
                HeaderNode("Header 3", "1", "XXYY"),
                HeaderNode("Header 4", "1", "XXYY"),
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine="mau",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
    ]

    assert par.headers == [
        HeaderNode("Header 1", "1", "XXYY"),
        HeaderNode("Header 2", "1", "XXYY"),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_engine_mau_multiple_blocks_are_independent(mock_header_anchor):
    mock_header_anchor.return_value = "XXYY"

    source = """
    = Header 1

    = Header 2

    [sometype, engine=mau]
    ----
    = Header 3

    = Header 4
    ----

    [sometype, engine=mau]
    ----
    = Header 5

    = Header 6
    ----
    """

    par = runner(source)

    assert par.nodes == [
        HeaderNode("Header 1", "1", "XXYY"),
        HeaderNode("Header 2", "1", "XXYY"),
        BlockNode(
            blocktype="sometype",
            content=[
                HeaderNode("Header 3", "1", "XXYY"),
                HeaderNode("Header 4", "1", "XXYY"),
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine="mau",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
        BlockNode(
            blocktype="sometype",
            content=[
                HeaderNode("Header 5", "1", "XXYY"),
                HeaderNode("Header 6", "1", "XXYY"),
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine="mau",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
    ]

    assert par.headers == [
        HeaderNode("Header 1", "1", "XXYY"),
        HeaderNode("Header 2", "1", "XXYY"),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_engine_mau_toc(mock_header_anchor):
    mock_header_anchor.return_value = "XXYY"

    source = """
    = Header 1

    = Header 2

    [sometype, engine=mau]
    ----
    = Header 3

    = Header 4

    ::toc:
    ----

    ::toc:
    """

    par = runner(source)

    assert par.nodes == [
        HeaderNode("Header 1", "1", "XXYY"),
        HeaderNode("Header 2", "1", "XXYY"),
        BlockNode(
            blocktype="sometype",
            content=[
                HeaderNode("Header 3", "1", "XXYY"),
                HeaderNode("Header 4", "1", "XXYY"),
                CommandTocNode(
                    [
                        HeaderNode("Header 3", "1", "XXYY"),
                        HeaderNode("Header 4", "1", "XXYY"),
                    ]
                ),
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine="mau",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
        CommandTocNode(
            [
                HeaderNode("Header 1", "1", "XXYY"),
                HeaderNode("Header 2", "1", "XXYY"),
            ]
        ),
    ]

    assert par.headers == [
        HeaderNode("Header 1", "1", "XXYY"),
        HeaderNode("Header 2", "1", "XXYY"),
    ]
