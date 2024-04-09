from mau.environment.environment import Environment
from mau.nodes.inline import TextNode
from mau.nodes.page import DocumentNode, HorizontalRuleNode
from mau.nodes.paragraph import ParagraphNode
from mau.visitors.base_visitor import BaseVisitor


def test_horizontal_rule_node():
    visitor = BaseVisitor(Environment())

    node = HorizontalRuleNode(
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "horizontal_rule",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
            "subtype": None,
        }
    }


def test_document_node():
    visitor = BaseVisitor(Environment())

    node = DocumentNode(
        children=[
            ParagraphNode(
                children=[TextNode("Just some text")],
                args=["arg1", "arg2"],
                kwargs={"key1": "value1"},
                tags=["tag1", "tag2"],
            )
        ],
        args=["arg3", "arg4"],
        kwargs={"key2": "value2"},
        tags=["tag3", "tag4"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "document",
            "content": [
                {
                    "data": {
                        "type": "paragraph",
                        "content": [
                            {
                                "data": {
                                    "type": "text",
                                    "value": "Just some text",
                                    "args": [],
                                    "kwargs": {},
                                    "subtype": None,
                                    "tags": [],
                                }
                            }
                        ],
                        "title": {},
                        "subtype": None,
                        "args": ["arg1", "arg2"],
                        "kwargs": {"key1": "value1"},
                        "tags": ["tag1", "tag2"],
                    }
                }
            ],
            "args": ["arg3", "arg4"],
            "kwargs": {"key2": "value2"},
            "tags": ["tag3", "tag4"],
            "subtype": None,
        }
    }
