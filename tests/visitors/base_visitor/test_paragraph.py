from mau.nodes.label import LabelNode
from mau.nodes.node import Node
from mau.nodes.paragraph import ParagraphLineNode, ParagraphNode
from mau.test_helpers import check_visit_node


def test_paragraph_line_node_without_content():
    node = ParagraphLineNode()

    expected = {
        "_type": "paragraph-line",
        "content": [],
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_paragraph_line_node_with_content():
    nodes: list[Node] = [Node(), Node()]
    labels = {"somelabel": LabelNode("somelabel", content=[Node()])}

    node = ParagraphLineNode(content=nodes, labels=labels)

    expected = {
        "_type": "paragraph-line",
        "content": [
            {
                "_type": "none",
                "kwargs": {},
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
            {
                "_type": "none",
                "kwargs": {},
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
        ],
        "labels": {
            "somelabel": {
                "_type": "label",
                "role": "somelabel",
                "content": [
                    {
                        "_type": "none",
                        "kwargs": {},
                        "subtype": None,
                        "tags": [],
                        "internal_tags": [],
                        "args": [],
                    }
                ],
                "kwargs": {},
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
        },
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_paragraph_node_without_content():
    node = ParagraphNode()

    expected = {
        "_type": "paragraph",
        "content": [],
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_paragraph_node_with_content():
    content: list[ParagraphLineNode] = [ParagraphLineNode(), ParagraphLineNode()]
    labels = {"somelabel": LabelNode("somelabel", content=[Node()])}

    node = ParagraphNode(content=content, labels=labels)

    expected = {
        "_type": "paragraph",
        "content": [
            {
                "_type": "paragraph-line",
                "content": [],
                "labels": {},
                "kwargs": {},
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
            {
                "_type": "paragraph-line",
                "content": [],
                "labels": {},
                "kwargs": {},
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
        ],
        "labels": {
            "somelabel": {
                "_type": "label",
                "role": "somelabel",
                "content": [
                    {
                        "_type": "none",
                        "kwargs": {},
                        "subtype": None,
                        "tags": [],
                        "internal_tags": [],
                        "args": [],
                    }
                ],
                "kwargs": {},
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
        },
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)
