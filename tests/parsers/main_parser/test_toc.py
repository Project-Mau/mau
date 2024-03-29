from unittest.mock import patch

from mau.lexers.main_lexer import MainLexer
from mau.nodes.header import HeaderNode
from mau.nodes.page import ContainerNode
from mau.nodes.toc import TocEntryNode, TocNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_command_toc():
    source = """
    [*subtype1, arg1, arg2, #tag1, key1=value1, key2=value2]
    ::toc:
    """

    assert runner(source).nodes == [
        TocNode(
            [],
            subtype="subtype1",
            args=["arg1", "arg2"],
            kwargs={"key1": "value1", "key2": "value2"},
            tags=["tag1"],
        ),
    ]


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
                TocNode(
                    children=[
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
        "toc": TocNode(
            children=[
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
