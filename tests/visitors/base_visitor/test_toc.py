from mau.environment.environment import Environment
from mau.nodes.toc import TocEntryNode, TocNode
from mau.visitors.base_visitor import BaseVisitor


def test_toc_node():
    visitor = BaseVisitor(Environment())

    node = TocNode(
        entries=[
            TocEntryNode(
                "Header 1",
                "header-1",
                children=[
                    TocEntryNode("Header 1.1", "header-1-1"),
                ],
            ),
            TocEntryNode("Header 2", "header-2"),
        ],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "toc",
            "entries": [
                {
                    "data": {
                        "anchor": "header-1",
                        "args": [],
                        "children": [
                            {
                                "data": {
                                    "anchor": "header-1-1",
                                    "args": [],
                                    "children": [],
                                    "kwargs": {},
                                    "tags": [],
                                    "type": "toc_entry",
                                    "value": "Header 1.1",
                                }
                            },
                        ],
                        "kwargs": {},
                        "tags": [],
                        "type": "toc_entry",
                        "value": "Header 1",
                    }
                },
                {
                    "data": {
                        "type": "toc_entry",
                        "anchor": "header-2",
                        "args": [],
                        "children": [],
                        "kwargs": {},
                        "tags": [],
                        "value": "Header 2",
                    }
                },
            ],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }
