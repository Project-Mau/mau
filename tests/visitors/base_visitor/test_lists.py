from mau.environment.environment import Environment
from mau.nodes.lists import ListItemNode, ListNode
from mau.visitors.base_visitor import BaseVisitor
from mau.nodes.inline import TextNode
from mau.visitors.base_visitor import BaseVisitor


def test_list_item_node():
    visitor = BaseVisitor(Environment())

    node = ListItemNode("4", TextNode("Just some text."))

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "list_item",
            "level": 4,
            "content": {
                "data": {
                    "type": "text",
                    "value": "Just some text.",
                }
            },
        }
    }


def test_list_node():
    visitor = BaseVisitor(Environment())

    node = ListNode(
        ordered=True,
        items=[ListItemNode("4", TextNode("Just some text."))],
        main_node=True,
        args=["arg1", "arg2"],
        kwargs={"key1": "value1", "start": 4},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "list",
            "items": [
                {
                    "data": {
                        "type": "list_item",
                        "level": 4,
                        "content": {
                            "data": {
                                "type": "text",
                                "value": "Just some text.",
                            }
                        },
                    }
                }
            ],
            "main_node": True,
            "ordered": True,
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1", "start": 4},
            "tags": ["tag1", "tag2"],
        }
    }
