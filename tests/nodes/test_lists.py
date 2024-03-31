from mau.nodes.inline import TextNode
from mau.nodes.lists import ListItemNode, ListNode


def test_list_item_node():
    node = ListItemNode(
        level="3", children=[TextNode("This is a list with one element")]
    )

    assert node.level == "3"
    assert node.children == [TextNode("This is a list with one element")]
    assert node.node_type == "list_item"
    assert node == ListItemNode(
        level="3", children=[TextNode("This is a list with one element")]
    )


def test_list_node():
    node = ListNode(ordered=True, main_node=False)

    assert node.ordered is True
    assert node.children == []
    assert node.main_node is False
    assert node.start == 1
    assert node.subtype is None
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "list"
    assert node == ListNode(ordered=True, main_node=False)


def test_list_node_with_start():
    node = ListNode(ordered=True, main_node=False, start=42)

    assert node.ordered is True
    assert node.children == []
    assert node.main_node is False
    assert node.start == 42
    assert node.subtype is None
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "list"
    assert node == ListNode(ordered=True, main_node=False, start=42)
