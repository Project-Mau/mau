from mau.nodes.inline import TextNode
from mau.nodes.lists import ListItemNode, ListNode


def test_list_item_node():
    node = ListItemNode("3", [TextNode("This is a list with one element")])

    assert node.level == "3"
    assert node.content == [TextNode("This is a list with one element")]
    assert node.node_type == "list_item"
    assert node == ListItemNode("3", [TextNode("This is a list with one element")])


def test_list_node():
    node = ListNode(ordered=True, main_node=False)

    assert node.ordered is True
    assert node.children == []
    assert node.main_node is False
    assert node.subtype is None
    assert node.args == []
    assert node.kwargs == {}
    assert node.node_type == "list"
    assert node == ListNode(ordered=True, main_node=False)
