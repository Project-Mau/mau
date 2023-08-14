from unittest.mock import Mock

from mau.nodes.nodes import Node, ValueNode


def test_node():
    node = Node()

    assert node.node_type == "node"
    assert node._content == {"type": "node"}


def test_value_node():
    node = ValueNode("somevalue")

    assert node.value == "somevalue"
    assert node.node_type == "value_node"
    assert node == ValueNode("somevalue")


def test_node_value_is_none_by_default():
    node = ValueNode()

    assert node.value is None
    assert node == ValueNode()


def test_node_accept():
    visitor = Mock()
    node = Node()
    node.node_type = "mynode"

    assert node.accept(visitor) == visitor._visit_mynode()


def test_node_accept_default():
    # This makes the Mock raise an AttributeError
    # for anything that is not in the list
    visitor = Mock(spec=["_visit_default"])
    node = Node()
    node.node_type = "mynode"

    assert node.accept(visitor) == visitor._visit_default()
