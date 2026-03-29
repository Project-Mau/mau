from mau.nodes.inline import TextNode
from mau.nodes.node import NodeInfo
from mau.parsers.buffers.label_buffer import LabelBuffer
from mau.test_helpers import (
    compare_nodes_sequence,
    generate_context,
)


def test_title_buffer():
    tb = LabelBuffer()

    assert tb.pop() == {}


def test_title_buffer_push_and_pop():
    tb = LabelBuffer()

    test_nodes = [
        TextNode(
            "Some title",
            info=NodeInfo(context=generate_context(0, 1, 0, 11)),
        )
    ]

    tb.push("title", test_nodes)

    children = tb.pop()

    assert list(children.keys()) == ["title"]

    compare_nodes_sequence(children["title"], test_nodes)

    assert tb.pop() == {}


def test_title_buffer_push_multiple_children():
    tb = LabelBuffer()

    title_nodes = [
        TextNode(
            "Some title",
            info=NodeInfo(context=generate_context(0, 0, 0, 10)),
        )
    ]

    source_nodes = [
        TextNode(
            "Some source",
            info=NodeInfo(context=generate_context(1, 0, 1, 11)),
        )
    ]

    tb.push("title", title_nodes)
    tb.push("source", source_nodes)

    children = tb.pop()

    assert list(children.keys()) == ["title", "source"]

    compare_nodes_sequence(children["title"], title_nodes)
    compare_nodes_sequence(children["source"], source_nodes)

    assert tb.pop() == {}


def test_title_buffer_push_twice_the_same_position():
    tb = LabelBuffer()

    title_nodes = [
        TextNode(
            "Some title",
            info=NodeInfo(context=generate_context(0, 0, 0, 10)),
        )
    ]

    title_nodes2 = [
        TextNode(
            "Some title 2",
            info=NodeInfo(context=generate_context(0, 0, 0, 10)),
        )
    ]

    tb.push("title", title_nodes)
    tb.push("title", title_nodes2)

    children = tb.pop()

    assert list(children.keys()) == ["title"]

    compare_nodes_sequence(children["title"], title_nodes2)

    assert tb.pop() == {}
