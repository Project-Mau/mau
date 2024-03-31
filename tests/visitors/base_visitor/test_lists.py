from mau.environment.environment import Environment
from mau.nodes.inline import TextNode
from mau.nodes.lists import ListItemNode, ListNode
from mau.visitors.base_visitor import BaseVisitor


def test_list_item_node():
    visitor = BaseVisitor(Environment())

    node = ListItemNode(level="4", children=[TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "list_item",
            "level": 4,
            "content": [
                {
                    "data": {
                        "type": "text",
                        "value": "Just some text.",
                        "args": [],
                        "kwargs": {},
                        "subtype": None,
                        "tags": [],
                    }
                }
            ],
            "args": [],
            "kwargs": {},
            "subtype": None,
            "tags": [],
        }
    }


def test_list_node():
    visitor = BaseVisitor(Environment())

    node = ListNode(
        ordered=True,
        main_node=True,
        start=42,
        children=[ListItemNode(level="4", children=[TextNode("Just some text.")])],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1", "start": 4},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "list",
            "start": 42,
            "items": [
                {
                    "data": {
                        "type": "list_item",
                        "level": 4,
                        "content": [
                            {
                                "data": {
                                    "type": "text",
                                    "value": "Just some text.",
                                    "args": [],
                                    "kwargs": {},
                                    "subtype": None,
                                    "tags": [],
                                }
                            }
                        ],
                        "args": [],
                        "kwargs": {},
                        "subtype": None,
                        "tags": [],
                    }
                }
            ],
            "main_node": True,
            "ordered": True,
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1", "start": 4},
            "tags": ["tag1", "tag2"],
            "subtype": None,
        }
    }
