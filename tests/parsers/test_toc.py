from mau.nodes.page import HeaderNode
from mau.nodes.toc import TocEntryNode, TocNode
from mau.parsers.toc import create_toc


def test_create_toc():
    headers_list = [
        HeaderNode("Header 1", "1", "header-1"),
        HeaderNode("Header 1.1", "2", "header-1-1"),
        HeaderNode("Header 1.2", "2", "header-1-2"),
        HeaderNode("Header 2", "1", "header-2"),
        HeaderNode("Header 2.1", "2", "header-2-1"),
        HeaderNode("Header 2.1.1", "3", "header-2-1-1"),
    ]

    assert create_toc(headers_list) == TocNode(
        entries=[
            TocEntryNode(
                value="Header 1",
                anchor="header-1",
                children=[
                    TocEntryNode(
                        value="Header 1.1",
                        anchor="header-1-1",
                        children=[],
                    ),
                    TocEntryNode(
                        value="Header 1.2",
                        anchor="header-1-2",
                        children=[],
                    ),
                ],
            ),
            TocEntryNode(
                value="Header 2",
                anchor="header-2",
                children=[
                    TocEntryNode(
                        value="Header 2.1",
                        anchor="header-2-1",
                        children=[
                            TocEntryNode(
                                value="Header 2.1.1",
                                anchor="header-2-1-1",
                                children=[],
                            ),
                        ],
                    ),
                ],
            ),
        ]
    )


def test_create_toc_orphan_nodes():
    headers_list = [
        HeaderNode("Header 1", "1", "header-1"),
        HeaderNode("Header 1.1.1", "3", "header-1-1-1"),
        HeaderNode("Header 1.2", "2", "header-1-2"),
    ]

    assert create_toc(headers_list) == TocNode(
        entries=[
            TocEntryNode(
                value="Header 1",
                anchor="header-1",
                children=[
                    TocEntryNode(
                        value="Header 1.1.1",
                        anchor="header-1-1-1",
                        children=[],
                    ),
                    TocEntryNode(
                        value="Header 1.2",
                        anchor="header-1-2",
                        children=[],
                    ),
                ],
            ),
        ]
    )
