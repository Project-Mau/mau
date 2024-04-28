from mau.environment.environment import Environment
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.toc import TocEntryNode, TocNode
from mau.visitors.base_visitor import BaseVisitor


def test_toc_node():
    visitor = BaseVisitor(Environment())

    node = TocNode(
        children=[
            TocEntryNode(
                value=SentenceNode(children=[TextNode("Header 1")]),
                anchor="header-1",
                children=[
                    TocEntryNode(
                        value=SentenceNode(children=[TextNode("Header 1.1")]),
                        anchor="header-1-1",
                    ),
                ],
            ),
            TocEntryNode(
                value=SentenceNode(children=[TextNode("Header 2")]),
                anchor="header-2",
            ),
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
                        "children": [
                            {
                                "data": {
                                    "anchor": "header-1-1",
                                    "children": [],
                                    "tags": [],
                                    "type": "toc_entry",
                                    "value": {
                                        "data": {
                                            "type": "sentence",
                                            "subtype": None,
                                            "args": [],
                                            "kwargs": {},
                                            "tags": [],
                                            "content": [
                                                {
                                                    "data": {
                                                        "type": "text",
                                                        "value": "Header 1.1",
                                                        "subtype": None,
                                                        "args": [],
                                                        "kwargs": {},
                                                        "tags": [],
                                                    }
                                                }
                                            ],
                                        }
                                    },
                                }
                            }
                        ],
                        "tags": [],
                        "type": "toc_entry",
                        "value": {
                            "data": {
                                "type": "sentence",
                                "subtype": None,
                                "args": [],
                                "kwargs": {},
                                "tags": [],
                                "content": [
                                    {
                                        "data": {
                                            "type": "text",
                                            "value": "Header 1",
                                            "subtype": None,
                                            "args": [],
                                            "kwargs": {},
                                            "tags": [],
                                        }
                                    }
                                ],
                            }
                        },
                    }
                },
                {
                    "data": {
                        "type": "toc_entry",
                        "anchor": "header-2",
                        "children": [],
                        "tags": [],
                        "value": {
                            "data": {
                                "type": "sentence",
                                "subtype": None,
                                "args": [],
                                "kwargs": {},
                                "tags": [],
                                "content": [
                                    {
                                        "data": {
                                            "type": "text",
                                            "value": "Header 2",
                                            "subtype": None,
                                            "args": [],
                                            "kwargs": {},
                                            "tags": [],
                                        }
                                    }
                                ],
                            }
                        },
                    }
                },
            ],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }
