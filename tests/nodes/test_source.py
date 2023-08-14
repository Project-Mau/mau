from mau.nodes.inline import TextNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode


def test_callouts_entry_node():
    node = CalloutsEntryNode("somemarker", "somevalue")

    assert node.marker == "somemarker"
    assert node.value == "somevalue"
    assert node.node_type == "callouts_entry"
    assert node == CalloutsEntryNode("somemarker", "somevalue")


def test_callout_node():
    node = CalloutNode("2", "somemarker")

    assert node.line == "2"
    assert node.marker == "somemarker"
    assert node.node_type == "callout"
    assert node == CalloutNode("2", "somemarker")


def test_source_node():
    node = SourceNode(
        code=[TextNode("somecode")],
        callouts=[CalloutsEntryNode("somemarker", "somevalue")],
        markers=[CalloutNode("2", "somemarker")],
    )

    assert node.code == [TextNode("somecode")]
    assert node.language == "text"
    assert node.callouts == [CalloutsEntryNode("somemarker", "somevalue")]
    assert node.delimiter == ":"
    assert node.markers == [CalloutNode("2", "somemarker")]
    assert node.highlights == []
    assert node.classes == []
    assert node.title is None
    assert node.preprocessor is None
    assert node.args == []
    assert node.kwargs == {}
    assert node.tags == []
    assert node.node_type == "source"
    assert node == SourceNode(
        code=[TextNode("somecode")],
        callouts=[CalloutsEntryNode("somemarker", "somevalue")],
        markers=[CalloutNode("2", "somemarker")],
    )
