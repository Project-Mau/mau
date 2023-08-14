from mau.nodes.inline import (
    ClassNode,
    ImageNode,
    LinkNode,
    ListItemNode,
    MacroNode,
    SentenceNode,
    StyleNode,
    TextNode,
    VerbatimNode,
    WordNode,
)


def test_word_node():
    node = WordNode("somevalue")

    assert node.value == "somevalue"
    assert node.node_type == "word"
    assert node == WordNode("somevalue")


def test_text_node():
    node = TextNode("somevalue")

    assert node.value == "somevalue"
    assert node.node_type == "text"
    assert node == TextNode("somevalue")


def test_verbatim_node():
    node = VerbatimNode("somevalue")

    assert node.value == "somevalue"
    assert node.node_type == "verbatim"
    assert node == VerbatimNode("somevalue")


def test_sentence_node():
    node = SentenceNode([VerbatimNode("somevalue"), TextNode("othervalue")])

    assert node.content == [VerbatimNode("somevalue"), TextNode("othervalue")]
    assert node.node_type == "sentence"
    assert node == SentenceNode([VerbatimNode("somevalue"), TextNode("othervalue")])


def test_style_node():
    node = StyleNode("mystyle", TextNode("othervalue"))

    assert node.value == "mystyle"
    assert node.content == TextNode("othervalue")
    assert node.node_type == "style"
    assert node == StyleNode("mystyle", TextNode("othervalue"))


def test_macro_node():
    node = MacroNode("aname", args=["value"], kwargs={"akey": "avalue"})

    assert node.name == "aname"
    assert node.args == ["value"]
    assert node.kwargs == {"akey": "avalue"}
    assert node.node_type == "macro"
    assert node == MacroNode("aname", args=["value"], kwargs={"akey": "avalue"})


def test_class_node():
    node = ClassNode(["class1", "class2"], TextNode("othervalue"))

    assert node.classes == ["class1", "class2"]
    assert node.content == TextNode("othervalue")
    assert node.node_type == "class"
    assert node == ClassNode(["class1", "class2"], TextNode("othervalue"))


def test_link_node():
    node = LinkNode("atarget", "sometext")

    assert node.target == "atarget"
    assert node.text == "sometext"
    assert node.node_type == "link"
    assert node == LinkNode("atarget", "sometext")


def test_link_node_no_text():
    node = LinkNode("atarget")

    assert node.target == "atarget"
    assert node.text is None
    assert node.node_type == "link"
    assert node == LinkNode("atarget")


def test_image_node():
    node = ImageNode("someuri", "somealttext", "width", "height")

    assert node.uri == "someuri"
    assert node.alt_text == "somealttext"
    assert node.width == "width"
    assert node.height == "height"
    assert node.node_type == "image"
    assert node == ImageNode("someuri", "somealttext", "width", "height")


def test_list_item_node():
    node = ListItemNode("3", "somecontent")

    assert node.level == "3"
    assert node.content == "somecontent"
    assert node.node_type == "list_item"
    assert node == ListItemNode("3", "somecontent")
