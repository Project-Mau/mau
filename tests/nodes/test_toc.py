from mau.nodes.toc import TocEntryNode, TocNode


def test_toc_entry_node():
    node = TocEntryNode(value="Header 1", anchor="header-1", children=[])

    assert node.value == "Header 1"
    assert node.anchor == "header-1"
    assert node.children == []
    assert node.node_type == "toc_entry"
    assert node == TocEntryNode(value="Header 1", anchor="header-1", children=[])


def test_toc_node():
    node = TocNode(
        entries=[],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.entries == []
    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "toc"
    assert node == TocNode(
        entries=[],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )
