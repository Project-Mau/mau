from mau.nodes.inline import RawNode, StyleNode, TextNode, VerbatimNode, WordNode


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


def test_raw_node():
    node = RawNode("somevalue")

    assert node.value == "somevalue"
    assert node.node_type == "raw"
    assert node == RawNode("somevalue")


def test_verbatim_node():
    node = VerbatimNode("somevalue")

    assert node.value == "somevalue"
    assert node.node_type == "verbatim"
    assert node == VerbatimNode("somevalue")


def test_style_node():
    node = StyleNode("mystyle", children=[TextNode("othervalue")])

    assert node.value == "mystyle"
    assert node.children == [TextNode("othervalue")]
    assert node.node_type == "style"
    assert node == StyleNode("mystyle", children=[TextNode("othervalue")])
