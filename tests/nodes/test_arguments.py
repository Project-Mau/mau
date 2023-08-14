from mau.nodes.arguments import NamedArgumentNode, UnnamedArgumentNode


def test_unnamed_argument_node_value():
    node = UnnamedArgumentNode("somevalue")

    assert node.value == "somevalue"
    assert node.node_type == "unnamed_argument"
    assert node == UnnamedArgumentNode("somevalue")


def test_named_argument_node_value():
    node = NamedArgumentNode("somekey", "somevalue")

    assert node.key == "somekey"
    assert node.value == "somevalue"
    assert node.node_type == "named_argument"
    assert node == NamedArgumentNode("somekey", "somevalue")
