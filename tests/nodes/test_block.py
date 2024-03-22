from mau.nodes.block import BlockNode


def test_block_node():
    node = BlockNode(subtype="sometype", content=[], secondary_content=[])

    assert node.subtype == "sometype"
    assert node.content == []
    assert node.secondary_content == []
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "block"
    assert node == BlockNode(subtype="sometype", content=[], secondary_content=[])
