import textwrap
from unittest.mock import patch

from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import ContainerNode, HeaderNode, ParagraphNode
from mau.nodes.toc import CommandTocNode, TocEntryNode
from mau.parsers.main_parser import MainParser
from mau.parsers.references import reference_anchor

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


@patch("mau.parsers.main_parser.header_anchor")
def test_toc(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    = Header 1
    == Header 1.1
    = Header 2

    ::toc:
    """

    parser = runner(source)

    assert parser.output == {
        "content": ContainerNode(
            [
                HeaderNode("Header 1", "1", "Header 1-XXXXXX"),
                HeaderNode("Header 1.1", "2", "Header 1.1-XXXXXX"),
                HeaderNode("Header 2", "1", "Header 2-XXXXXX"),
                CommandTocNode(
                    entries=[
                        TocEntryNode(
                            value="Header 1",
                            anchor="Header 1-XXXXXX",
                            children=[
                                TocEntryNode(
                                    value="Header 1.1",
                                    anchor="Header 1.1-XXXXXX",
                                    children=[],
                                ),
                            ],
                        ),
                        TocEntryNode(
                            value="Header 2",
                            anchor="Header 2-XXXXXX",
                            children=[],
                        ),
                    ]
                ),
            ]
        ),
        "footnotes": [],
        "references": {},
        "toc": CommandTocNode(
            entries=[
                TocEntryNode(
                    value="Header 1",
                    anchor="Header 1-XXXXXX",
                    children=[
                        TocEntryNode(
                            value="Header 1.1",
                            anchor="Header 1.1-XXXXXX",
                            children=[],
                        ),
                    ],
                ),
                TocEntryNode(
                    value="Header 2",
                    anchor="Header 2-XXXXXX",
                    children=[],
                ),
            ]
        ),
        "custom_filters": {},
    }
