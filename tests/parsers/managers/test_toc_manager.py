from unittest.mock import call, patch

from mau.nodes.header import HeaderNode
from mau.nodes.include import (
    TocItemNode,
    TocNode,
)
from mau.nodes.node import Node
from mau.parsers.managers.toc_manager import (
    TocManager,
    add_nodes_under_level,
)
from mau.test_helpers import compare_nodes_sequence


def test_toc_manager_init():
    tm = TocManager()

    assert tm.headers == []
    assert tm.toc_nodes == []


def test_toc_manager_add_header():
    tm = TocManager()
    header_node = HeaderNode(level=1)

    tm.add_header(header_node)

    assert tm.headers == [header_node]


def test_toc_manager_add_toc_node():
    tm = TocManager()
    toc_node = TocNode()

    tm.add_toc_node(toc_node)

    assert tm.toc_nodes == [toc_node]


def test_toc_manager_update():
    tm = TocManager()
    header_node = HeaderNode(1)
    toc_node = TocNode()
    tm.add_header(header_node)
    tm.add_toc_node(toc_node)

    other_tm = TocManager()
    other_tm.update(tm)

    assert other_tm.headers == [header_node]
    assert other_tm.toc_nodes == [toc_node]


def test_add_nodes_without_nesting():
    parent_node = Node()

    node_header_a = HeaderNode(1, "A")
    node_header_b = HeaderNode(1, "B")
    node_header_c = HeaderNode(1, "C")

    nodes = [
        node_header_a,
        node_header_b,
        node_header_c,
    ]

    children: list[TocItemNode] = []

    idx = add_nodes_under_level(0, nodes, 0, children, parent_node)

    assert idx == len(nodes)

    node_toc_item_a = children[0]
    node_toc_item_b = children[1]
    node_toc_item_c = children[2]

    compare_nodes_sequence(
        children, [node_toc_item_a, node_toc_item_b, node_toc_item_c]
    )

    assert node_toc_item_a.parent == parent_node
    assert node_toc_item_b.parent == parent_node
    assert node_toc_item_c.parent == parent_node


def test_add_nodes_with_nesting():
    parent_node = Node()

    node_header_a = HeaderNode(1, "A")
    node_header_b = HeaderNode(2, "B")
    node_header_c = HeaderNode(3, "C")
    node_header_d = HeaderNode(2, "D")
    node_header_e = HeaderNode(2, "E")
    node_header_f = HeaderNode(1, "F")
    node_header_g = HeaderNode(3, "G")

    nodes = [
        node_header_a,
        node_header_b,
        node_header_c,
        node_header_d,
        node_header_e,
        node_header_f,
        node_header_g,
    ]

    children: list[TocItemNode] = []

    idx = add_nodes_under_level(0, nodes, 0, children, parent=parent_node)

    assert idx == len(nodes)

    node_toc_item_a = children[0]
    node_toc_item_f = children[1]
    node_toc_item_b = node_toc_item_a.entries[0]
    node_toc_item_d = node_toc_item_a.entries[1]
    node_toc_item_e = node_toc_item_a.entries[2]
    node_toc_item_c = node_toc_item_b.entries[0]
    node_toc_item_g = node_toc_item_f.entries[0]

    compare_nodes_sequence(children, [node_toc_item_a, node_toc_item_f])

    assert node_toc_item_a.parent == parent_node
    assert node_toc_item_b.parent == parent_node
    assert node_toc_item_c.parent == parent_node
    assert node_toc_item_d.parent == parent_node
    assert node_toc_item_e.parent == parent_node
    assert node_toc_item_f.parent == parent_node
    assert node_toc_item_g.parent == parent_node


def test_add_nodes_under_level_starts_with_any_level():
    parent_node = Node()

    node_header_a = HeaderNode(3, "A")
    node_header_b = HeaderNode(2, "B")
    node_header_c = HeaderNode(3, "C")

    node_toc_item_c = TocItemNode(node_header_c)
    node_toc_item_b = TocItemNode(node_header_b, entries=[node_toc_item_c])
    node_toc_item_a = TocItemNode(node_header_a)

    nodes = [
        node_header_a,
        node_header_b,
        node_header_c,
    ]

    children: list[TocItemNode] = []

    idx = add_nodes_under_level(0, nodes, 0, children, parent=parent_node)

    assert idx == len(nodes)

    compare_nodes_sequence(children, [node_toc_item_a, node_toc_item_b])


def test_add_nodes_under_level_can_terminate_with_single_node():
    parent_node = Node()

    node_header_a = HeaderNode(3, "A")
    node_header_b = HeaderNode(2, "B")
    node_header_c = HeaderNode(1, "C")

    node_toc_item_a = TocItemNode(node_header_a)
    node_toc_item_b = TocItemNode(node_header_b)
    node_toc_item_c = TocItemNode(node_header_c)

    nodes = [
        node_header_a,
        node_header_b,
        node_header_c,
    ]

    children: list[TocItemNode] = []

    idx = add_nodes_under_level(0, nodes, 0, children, parent=parent_node)

    assert idx == len(nodes)

    compare_nodes_sequence(
        children, [node_toc_item_a, node_toc_item_b, node_toc_item_c]
    )


@patch("mau.parsers.managers.toc_manager.default_header_internal_id")
def test_process(mock_default_header_internal_id):
    mock_default_header_internal_id.return_value = "some_uid"

    node_header_a = HeaderNode(1)
    node_header_b = HeaderNode(2)

    node_toc_item_b = TocItemNode(node_header_b)
    node_toc_item_a = TocItemNode(node_header_a, entries=[node_toc_item_b])

    header_nodes = [
        node_header_a,
        node_header_b,
    ]

    tm = TocManager()
    tm.headers = header_nodes
    test_toc_node = TocNode()
    tm.add_toc_node(test_toc_node)

    tm.process()

    compare_nodes_sequence(test_toc_node.plain_entries, header_nodes)
    compare_nodes_sequence(test_toc_node.nested_entries, [node_toc_item_a])

    assert mock_default_header_internal_id.mock_calls == [
        call(node_header_a),
        call(node_header_b),
    ]


def test_process_internal_id():
    node_header_a = HeaderNode(1, "A")
    node_header_b = HeaderNode(2, "B")

    node_toc_item_b = TocItemNode(node_header_b)
    node_toc_item_a = TocItemNode(node_header_a, entries=[node_toc_item_b])

    header_nodes = [
        node_header_a,
        node_header_b,
    ]

    tm = TocManager()
    tm.headers = header_nodes
    test_toc_node = TocNode()
    tm.add_toc_node(test_toc_node)

    tm.process()

    compare_nodes_sequence(test_toc_node.plain_entries, header_nodes)
    compare_nodes_sequence(test_toc_node.nested_entries, [node_toc_item_a])
