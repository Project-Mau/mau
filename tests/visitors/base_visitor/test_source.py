from mau.nodes.source import (
    SourceLineNode,
    SourceMarkerNode,
    SourceNode,
)
from mau.test_helpers import check_visit_node


def test_source_line_marker_node():
    node = SourceMarkerNode("somemarker")

    expected = {
        "_type": "source-marker",
        "value": "somemarker",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_source_line_node():
    node = SourceLineNode("42", "somecontent")

    expected = {
        "_type": "source-line",
        "line_number": "42",
        "line_content": "somecontent",
        "highlight_style": None,
        "marker": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_source_line_node_with_marker():
    marker_node = SourceMarkerNode("somemarker")
    node = SourceLineNode("42", "somecontent", marker=marker_node)

    expected = {
        "_type": "source-line",
        "line_number": "42",
        "line_content": "somecontent",
        "highlight_style": None,
        "marker": {
            "_type": "source-marker",
            "value": "somemarker",
            "kwargs": {},
            "subtype": None,
            "tags": [],
            "internal_tags": [],
            "args": [],
        },
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_source_node():
    node = SourceNode("somelanguage")

    expected = {
        "_type": "source",
        "language": "somelanguage",
        "classes": [],
        "content": [],
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)
