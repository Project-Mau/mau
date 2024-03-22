from mau.nodes.inline import TextNode
from mau.nodes.macros import MacroClassNode, MacroImageNode, MacroLinkNode, MacroNode


def test_macro_node():
    node = MacroNode("aname", args=["value"], kwargs={"akey": "avalue"})

    assert node.name == "aname"
    assert node.args == ["value"]
    assert node.kwargs == {"akey": "avalue"}
    assert node.node_type == "macro"
    assert node == MacroNode("aname", args=["value"], kwargs={"akey": "avalue"})


def test_class_node():
    node = MacroClassNode(["class1", "class2"], TextNode("othervalue"))

    assert node.classes == ["class1", "class2"]
    assert node.content == TextNode("othervalue")
    assert node.node_type == "macro__class"
    assert node == MacroClassNode(["class1", "class2"], TextNode("othervalue"))


def test_link_node():
    node = MacroLinkNode("atarget", "sometext")

    assert node.target == "atarget"
    assert node.text == "sometext"
    assert node.node_type == "macro__link"
    assert node == MacroLinkNode("atarget", "sometext")


def test_link_node_no_text():
    node = MacroLinkNode("atarget")

    assert node.target == "atarget"
    assert node.text is None
    assert node.node_type == "macro__link"
    assert node == MacroLinkNode("atarget")


def test_image_node():
    node = MacroImageNode("someuri", "somealttext", "width", "height")

    assert node.uri == "someuri"
    assert node.alt_text == "somealttext"
    assert node.width == "width"
    assert node.height == "height"
    assert node.node_type == "macro__image"
    assert node == MacroImageNode("someuri", "somealttext", "width", "height")
