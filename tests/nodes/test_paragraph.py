from mau.nodes.inline import TextNode
from mau.nodes.paragraph import ParagraphNode


def test_paragraph_node():
    node = ParagraphNode(
        children=[TextNode("sometext")],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.children == [TextNode("sometext")]
    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "paragraph"
    assert node == ParagraphNode(
        children=[TextNode("sometext")],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )
