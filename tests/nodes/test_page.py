from mau.nodes.page import ContainerNode, DocumentNode, HorizontalRuleNode


def test_horizontal_rule_node():
    node = HorizontalRuleNode(
        subtype="type1",
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )

    assert node.subtype == "type1"
    assert node.args == ["value1", "value2"]
    assert node.tags == ["tag1", "tag2"]
    assert node.kwargs == {"key1": "text1", "key2": "text2"}
    assert node.node_type == "horizontal_rule"
    assert node == HorizontalRuleNode(
        subtype="type1",
        args=["value1", "value2"],
        tags=["tag1", "tag2"],
        kwargs={"key1": "text1", "key2": "text2"},
    )


def test_container_node():
    node = ContainerNode()

    assert node.children == []
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "container"
    assert node == ContainerNode()


def test_document_node():
    node = DocumentNode()

    assert node.children == []
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "document"
    assert node == DocumentNode()
