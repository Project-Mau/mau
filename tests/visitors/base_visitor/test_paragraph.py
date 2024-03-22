from mau.nodes.paragraph import ParagraphNode
from mau.visitors.base_visitor import BaseVisitor
from mau.environment.environment import Environment
from mau.nodes.inline import TextNode


def test_paragraph_node():
    visitor = BaseVisitor(Environment())

    node = ParagraphNode(
        TextNode("Just some text"),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "paragraph",
            "content": {
                "data": {
                    "type": "text",
                    "value": "Just some text",
                }
            },
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }
