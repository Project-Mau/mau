from mau.environment.environment import Environment
from mau.nodes.footnotes import FootnoteNode, FootnotesNode
from mau.nodes.inline import TextNode
from mau.visitors.base_visitor import BaseVisitor


def test_footnotes():
    visitor = BaseVisitor(Environment())

    node = FootnotesNode(
        children=[
            FootnoteNode(
                children=[TextNode("Footnote 1")],
                number="1",
                reference_anchor="anchor-1",
                content_anchor="anchor-1-def",
            ).to_entry(),
            FootnoteNode(
                children=[TextNode("Footnote 2")],
                number="2",
                reference_anchor="anchor-2",
                content_anchor="anchor-2-def",
            ).to_entry(),
        ],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "footnotes",
            "entries": [
                {
                    "data": {
                        "content": [
                            {
                                "data": {
                                    "type": "text",
                                    "value": "Footnote 1",
                                    "args": [],
                                    "kwargs": {},
                                    "subtype": None,
                                    "tags": [],
                                }
                            },
                        ],
                        "content_anchor": "anchor-1-def",
                        "number": "1",
                        "reference_anchor": "anchor-1",
                        "type": "footnotes_entry",
                        "args": [],
                        "kwargs": {},
                        "subtype": None,
                        "tags": [],
                    }
                },
                {
                    "data": {
                        "content": [
                            {
                                "data": {
                                    "type": "text",
                                    "value": "Footnote 2",
                                    "args": [],
                                    "kwargs": {},
                                    "subtype": None,
                                    "tags": [],
                                }
                            },
                        ],
                        "content_anchor": "anchor-2-def",
                        "number": "2",
                        "reference_anchor": "anchor-2",
                        "type": "footnotes_entry",
                        "args": [],
                        "kwargs": {},
                        "subtype": None,
                        "tags": [],
                    }
                },
            ],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
            "subtype": None,
        }
    }
