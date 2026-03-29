from mau.nodes.block import BlockNode
from mau.test_helpers import check_visit_node


def test_block_node():
    node = BlockNode()

    expected = {
        "_type": "block",
        "classes": [],
        "labels": {},
        "content": [],
        "args": [],
        "kwargs": {},
        "tags": [],
        "internal_tags": [],
        "subtype": None,
    }

    check_visit_node(node, expected)
