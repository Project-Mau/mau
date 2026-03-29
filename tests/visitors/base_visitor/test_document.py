from mau.nodes.document import (
    DocumentNode,
    HorizontalRuleNode,
)
from mau.test_helpers import check_visit_node


def test_horizontal_rule_node():
    node = HorizontalRuleNode()

    expected = {
        "_type": "horizontal-rule",
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_document_node():
    node = DocumentNode()

    expected = {
        "_type": "document",
        "content": [],
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)
