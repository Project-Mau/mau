from mau.nodes.raw import RawLineNode, RawNode
from mau.test_helpers import check_visit_node


def test_raw_content_line_node():
    node = RawLineNode("somevalue")

    expected = {
        "_type": "raw-line",
        "value": "somevalue",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_raw_content_node():
    line1 = RawLineNode("somevalue1")
    line2 = RawLineNode("somevalue2")
    node = RawNode(content=[line1, line2])

    expected = {
        "_type": "raw",
        "classes": [],
        "labels": {},
        "content": [
            {
                "_type": "raw-line",
                "value": "somevalue1",
                "kwargs": {},
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
            {
                "_type": "raw-line",
                "value": "somevalue2",
                "kwargs": {},
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
        ],
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)
