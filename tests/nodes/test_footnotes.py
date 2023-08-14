from mau.nodes.footnotes import CommandFootnotesNode, FootnoteNode, FootnotesEntryNode
from mau.nodes.inline import TextNode, VerbatimNode


def test_footnote_node():
    node = FootnoteNode([VerbatimNode("somevalue"), TextNode("othervalue")])

    assert node.content == [VerbatimNode("somevalue"), TextNode("othervalue")]
    assert node.number is None
    assert node.reference_anchor is None
    assert node.content_anchor is None
    assert node.node_type == "footnote"
    assert node == FootnoteNode([VerbatimNode("somevalue"), TextNode("othervalue")])


def test_footnote_node_with_number_and_anchor():
    node = FootnoteNode(
        [VerbatimNode("somevalue"), TextNode("othervalue")],
        number="3",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )

    assert node.content == [VerbatimNode("somevalue"), TextNode("othervalue")]
    assert node.number == "3"
    assert node.reference_anchor == "someanchor"
    assert node.content_anchor == "someanchor-def"
    assert node.node_type == "footnote"
    assert node == FootnoteNode(
        [VerbatimNode("somevalue"), TextNode("othervalue")],
        number="3",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )


def test_footnotes_entry_node():
    node = FootnotesEntryNode(
        content=TextNode("Some text"),
        number="1",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )

    assert node.content == TextNode("Some text")
    assert node.number == "1"
    assert node.reference_anchor == "someanchor"
    assert node.content_anchor == "someanchor-def"
    assert node.node_type == "footnotes_entry"
    assert node == FootnotesEntryNode(
        content=TextNode("Some text"),
        number="1",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )


def test_command_footnotes_node():
    node = CommandFootnotesNode(
        entries=[TextNode("somevalue1"), TextNode("somevalue2")],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.entries == [TextNode("somevalue1"), TextNode("somevalue2")]
    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "command_footnotes"
    assert node == CommandFootnotesNode(
        entries=[TextNode("somevalue1"), TextNode("somevalue2")],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )
