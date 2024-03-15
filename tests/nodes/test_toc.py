from mau.nodes.page import HeaderNode
from mau.nodes.toc import CommandTocNode, TocEntryNode


def test_toc_entry_node():
    node = TocEntryNode(value="Header 1", anchor="header-1", children=[])

    assert node.value == "Header 1"
    assert node.anchor == "header-1"
    assert node.children == []
    assert node.node_type == "toc_entry"
    assert node == TocEntryNode(value="Header 1", anchor="header-1", children=[])


def test_command_toc_node():
    node = CommandTocNode(
        entries=[
            HeaderNode(
                "somevalue",
                "somelevel",
                "someanchor",
                args=["hvalue1", "hvalue2"],
                kwargs={"hkey1": "htext1", "hkey2": "htext2"},
            )
        ],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.entries == [
        HeaderNode(
            "somevalue",
            "somelevel",
            "someanchor",
            args=["hvalue1", "hvalue2"],
            kwargs={"hkey1": "htext1", "hkey2": "htext2"},
        )
    ]
    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "command_toc"
    assert node == CommandTocNode(
        entries=[
            HeaderNode(
                "somevalue",
                "somelevel",
                "someanchor",
                args=["hvalue1", "hvalue2"],
                kwargs={"hkey1": "htext1", "hkey2": "htext2"},
            )
        ],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )
