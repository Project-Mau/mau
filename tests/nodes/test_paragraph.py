from mau.nodes.paragraph import ParagraphNode
from mau.nodes.inline import SentenceNode, TextNode


def test_paragraph_node():
    node = ParagraphNode(
        SentenceNode([TextNode("sometext")]),
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.content == SentenceNode([TextNode("sometext")])
    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "paragraph"
    assert node == ParagraphNode(
        SentenceNode([TextNode("sometext")]),
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )
