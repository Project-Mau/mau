from mau.environment.environment import Environment
from mau.nodes.content import ContentImageNode, ContentNode
from mau.nodes.inline import TextNode
from mau.visitors.base_visitor import BaseVisitor


def test_content_node():
    visitor = BaseVisitor(Environment())

    node = ContentNode(
        content_type="sometype",
        title=TextNode("sometitle"),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "content",
            "content_type": "sometype",
            "title": {
                "data": {
                    "type": "text",
                    "value": "sometitle",
                }
            },
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_content_image_node():
    visitor = BaseVisitor(Environment())

    node = ContentImageNode(
        uri="someuri",
        alt_text="sometext",
        classes=["class1", "class2"],
        title=TextNode("sometitle"),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "content_image",
            "uri": "someuri",
            "title": {
                "data": {
                    "type": "text",
                    "value": "sometitle",
                }
            },
            "alt_text": "sometext",
            "classes": ["class1", "class2"],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }
