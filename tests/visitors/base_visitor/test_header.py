from mau.environment.environment import Environment
from mau.nodes.header import HeaderNode
from mau.visitors.base_visitor import BaseVisitor


def test_header_node():
    visitor = BaseVisitor(Environment())

    node = HeaderNode(
        value="Just some text",
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
            "value": "Just some text",
            "level": 3,
            "anchor": "someanchor",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }
