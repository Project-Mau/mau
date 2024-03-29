from unittest.mock import Mock

from mau.nodes.nodes import SupaNode, SupaValueNode


def test_node():
    node = SupaNode()

    assert node.node_type == "node"
    assert node.asdict() == {
        "type": "node",
        "subtype": None,
        "children": [],
        "args": [],
        "kwargs": {},
        "tags": [],
    }


def test_value_node():
    node = SupaValueNode("somevalue")

    assert node.value == "somevalue"
    assert node.node_type == "value_node"
    assert node == SupaValueNode("somevalue")


def test_node_accept():
    visitor = Mock()
    node = SupaNode()
    node.node_type = "mynode"

    assert node.accept(visitor) == visitor._visit_mynode()


def test_node_accept_default():
    # This makes the Mock raise an AttributeError
    # for anything that is not in the list
    visitor = Mock(spec=["_visit_default"])
    node = SupaNode()
    node.node_type = "mynode"

    assert node.accept(visitor) == visitor._visit_default()
