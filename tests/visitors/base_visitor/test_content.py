from mau.environment.environment import Environment
from mau.nodes.content import ContentImageNode, ContentNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.visitors.base_visitor import BaseVisitor


def test_content_node():
    visitor = BaseVisitor(Environment())

    node = ContentNode(
        content_type="sometype",
        uris=["/uri1", "/uri2"],
        title=SentenceNode(children=[TextNode("sometitle")]),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "content",
            "content_type": "sometype",
            "uris": ["/uri1", "/uri2"],
            "title": {
                "data": {
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "sometitle",
                                "args": [],
                                "kwargs": {},
                                "subtype": None,
                                "tags": [],
                            }
                        },
                    ],
                    "type": "sentence",
                    "args": [],
                    "kwargs": {},
                    "subtype": None,
                    "tags": [],
                },
            },
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
            "subtype": None,
        }
    }


def test_content_image_node():
    visitor = BaseVisitor(Environment())

    node = ContentImageNode(
        uri="someuri",
        alt_text="sometext",
        classes=["class1", "class2"],
        title=SentenceNode(children=[TextNode("sometitle")]),
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
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "sometitle",
                                "args": [],
                                "kwargs": {},
                                "subtype": None,
                                "tags": [],
                            }
                        },
                    ],
                    "type": "sentence",
                    "args": [],
                    "kwargs": {},
                    "subtype": None,
                    "tags": [],
                },
            },
            "alt_text": "sometext",
            "classes": ["class1", "class2"],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
            "subtype": None,
        }
    }
