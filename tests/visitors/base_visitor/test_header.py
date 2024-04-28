from mau.environment.environment import Environment
from mau.nodes.header import HeaderNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.visitors.base_visitor import BaseVisitor


def test_header_node():
    visitor = BaseVisitor(Environment())

    node = HeaderNode(
        value=SentenceNode(children=[TextNode("Just some text")]),
        level="3",
        anchor="someanchor",
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "header",
            "value": {
                "data": {
                    "type": "sentence",
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "Just some text",
                                "subtype": None,
                                "args": [],
                                "kwargs": {},
                                "tags": [],
                            },
                        }
                    ],
                    "subtype": None,
                    "args": [],
                    "kwargs": {},
                    "tags": [],
                }
            },
            "level": 3,
            "anchor": "someanchor",
            "subtype": None,
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }
