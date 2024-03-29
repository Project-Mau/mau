from mau.nodes.block import BlockNode


def test_block_node():
    node = BlockNode(subtype="sometype")

    assert node.subtype == "sometype"
    assert node.children == []
    assert node.secondary_children == []
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "block"
    assert node == BlockNode(subtype="sometype")
