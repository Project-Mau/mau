from mau.nodes.inline import TextNode, VerbatimNode
from mau.nodes.references import ReferenceNode, ReferencesEntryNode, ReferencesNode


def test_reference_node():
    node = ReferenceNode(
        "somecontent",
        children=[VerbatimNode("somevalue"), TextNode("othervalue")],
    )

    assert node.content_type == "somecontent"
    assert node.children == [VerbatimNode("somevalue"), TextNode("othervalue")]
    assert node.number is None
    assert node.title is None
    assert node.reference_anchor is None
    assert node.content_anchor is None
    assert node.node_type == "reference"
    assert node == ReferenceNode(
        "somecontent",
        children=[VerbatimNode("somevalue"), TextNode("othervalue")],
    )


def test_reference_node_with_number_and_anchor():
    node = ReferenceNode(
        "somecontent",
        children=[VerbatimNode("somevalue"), TextNode("othervalue")],
        number="3",
        title="Exercise 1",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )

    assert node.content_type == "somecontent"
    assert node.children == [VerbatimNode("somevalue"), TextNode("othervalue")]
    assert node.number == "3"
    assert node.reference_anchor == "someanchor"
    assert node.content_anchor == "someanchor-def"
    assert node.node_type == "reference"
    assert node == ReferenceNode(
        "somecontent",
        children=[VerbatimNode("somevalue"), TextNode("othervalue")],
        number="3",
        title="Exercise 1",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )


def test_references_entry_node():
    node = ReferencesEntryNode(
        "somecontent",
        children=[TextNode("Some text")],
        number="1",
        title="Exercise 1",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )

    assert node.content_type == "somecontent"
    assert node.children == [TextNode("Some text")]
    assert node.number == "1"
    assert node.title == "Exercise 1"
    assert node.reference_anchor == "someanchor"
    assert node.content_anchor == "someanchor-def"
    assert node.node_type == "references_entry"
    assert node == ReferencesEntryNode(
        "somecontent",
        children=[TextNode("Some text")],
        number="1",
        title="Exercise 1",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )


def test_references_node():
    node = ReferencesNode(
        content_type="somecontent",
        children=[TextNode("somevalue1"), TextNode("somevalue2")],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.children == [TextNode("somevalue1"), TextNode("somevalue2")]
    assert node.content_type == "somecontent"
    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "references"
    assert node == ReferencesNode(
        content_type="somecontent",
        children=[TextNode("somevalue1"), TextNode("somevalue2")],
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )
