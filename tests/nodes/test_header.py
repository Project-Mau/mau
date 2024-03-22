from mau.nodes.header import HeaderNode


def test_header_node():
    node = HeaderNode(
        "somevalue",
        "somelevel",
        "someanchor",
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.value == "somevalue"
    assert node.level == "somelevel"
    assert node.anchor == "someanchor"
    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "header"
    assert node == HeaderNode(
        "somevalue",
        "somelevel",
        "someanchor",
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )
