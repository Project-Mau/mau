from mau.nodes.header import HeaderNode
from mau.nodes.inline import TextNode
from mau.nodes.macros import (
    MacroClassNode,
    MacroHeaderNode,
    MacroImageNode,
    MacroLinkNode,
    MacroNode,
)


def test_macro_node():
    node = MacroNode("aname", args=["value"], kwargs={"akey": "avalue"})

    assert node.name == "aname"
    assert node.args == ["value"]
    assert node.kwargs == {"akey": "avalue"}
    assert node.node_type == "macro"
    assert node == MacroNode("aname", args=["value"], kwargs={"akey": "avalue"})


def test_class_node():
    node = MacroClassNode(["class1", "class2"], children=[TextNode("othervalue")])

    assert node.classes == ["class1", "class2"]
    assert node.children == [TextNode("othervalue")]
    assert node.node_type == "macro.class"
    assert node == MacroClassNode(
        ["class1", "class2"], children=[TextNode("othervalue")]
    )


def test_link_node():
    node = MacroLinkNode("atarget", children=[TextNode("sometext")])

    assert node.target == "atarget"
    assert node.children == [TextNode("sometext")]
    assert node.node_type == "macro.link"
    assert node == MacroLinkNode("atarget", children=[TextNode("sometext")])


def test_link_node_no_text():
    node = MacroLinkNode("atarget")

    assert node.target == "atarget"
    assert node.children == []
    assert node.node_type == "macro.link"
    assert node == MacroLinkNode("atarget")


def test_image_node():
    node = MacroImageNode("someuri", "somealttext", "width", "height")

    assert node.uri == "someuri"
    assert node.alt_text == "somealttext"
    assert node.width == "width"
    assert node.height == "height"
    assert node.node_type == "macro.image"
    assert node == MacroImageNode("someuri", "somealttext", "width", "height")


def test_header_node():
    header_node = HeaderNode("someheader", "1", "someanchor")
    node = MacroHeaderNode("someid", header_node, children=[TextNode("sometext")])

    assert node.header_id == "someid"
    assert node.header == header_node
    assert node.children == [TextNode("sometext")]
    assert node.node_type == "macro.header"
    assert node == MacroHeaderNode(
        "someid", header_node, children=[TextNode("sometext")]
    )
