from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import (
    BlockNode,
    ContainerNode,
    ContentImageNode,
    ContentNode,
    DocumentNode,
    HeaderNode,
    HorizontalRuleNode,
    PageNode,
)


def test_page_node():
    node = PageNode(
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "page_node"
    assert node == PageNode(
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )


def test_horizontal_rule_node():
    node = HorizontalRuleNode(
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "horizontal_rule"
    assert node == HorizontalRuleNode(
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )


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


def test_content_node():
    node = ContentNode(content_type="somecontent", title="sometitle")

    assert node.content_type == "somecontent"
    assert node.title == "sometitle"
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "content"
    assert node == ContentNode(content_type="somecontent", title="sometitle")


def test_content_image_node():
    node = ContentImageNode(
        uri="someuri", alt_text="somealttext", classes=[], title="sometitle"
    )

    assert node.uri == "someuri"
    assert node.alt_text == "somealttext"
    assert node.classes == []
    assert node.title == "sometitle"
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "content_image"
    assert node == ContentImageNode(
        uri="someuri", alt_text="somealttext", classes=[], title="sometitle"
    )


def test_block_node():
    node = BlockNode(subtype="sometype", content=[], secondary_content=[])

    assert node.subtype == "sometype"
    assert node.content == []
    assert node.secondary_content == []
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "block"
    assert node == BlockNode(subtype="sometype", content=[], secondary_content=[])


def test_container_node():
    node = ContainerNode(content=[])

    assert node.content == []
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "container"
    assert node == ContainerNode(content=[])


def test_document_node():
    node = DocumentNode(content=[])

    assert node.content == []
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "document"
    assert node == DocumentNode(content=[])
