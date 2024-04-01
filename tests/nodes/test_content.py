from mau.nodes.content import ContentImageNode, ContentNode


def test_content_node():
    node = ContentNode(
        content_type="somecontent", uris=["/uri1", "/uri2"], title="sometitle"
    )

    assert node.content_type == "somecontent"
    assert node.uris == ["/uri1", "/uri2"]
    assert node.title == "sometitle"
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "content"
    assert node == ContentNode(
        content_type="somecontent", uris=["/uri1", "/uri2"], title="sometitle"
    )


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
