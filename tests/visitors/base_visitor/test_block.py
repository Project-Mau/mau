from mau.environment.environment import Environment
from mau.nodes.block import BlockNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.visitors.base_visitor import BaseVisitor


def test_block_node_standard_block_template():
    visitor = BaseVisitor(Environment())

    node = BlockNode(
        subtype="someblock",
        children=[TextNode("my content")],
        secondary_children=[TextNode("my secondary content")],
        classes=["class1", "class2"],
        title=SentenceNode(children=[TextNode("sometitle")]),
        engine="someengine",
        preprocessor="somepreprocessor",
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "block",
            "subtype": "someblock",
            "content": [
                {
                    "data": {
                        "type": "text",
                        "value": "my content",
                    }
                }
            ],
            "secondary_content": [
                {
                    "data": {
                        "type": "text",
                        "value": "my secondary content",
                    }
                }
            ],
            "classes": ["class1", "class2"],
            "title": {
                "data": {
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "sometitle",
                            }
                        },
                    ],
                    "type": "sentence",
                },
            },
            "engine": "someengine",
            "preprocessor": "somepreprocessor",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }
