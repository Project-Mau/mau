from mau.nodes.inline import (
    StyleNode,
    TextNode,
    VerbatimNode,
    WordNode,
)
from mau.test_helpers import check_node_with_content, check_visit_node


def test_word_node():
    node = WordNode("somevalue")

    expected = {
        "_type": "word",
        "value": "somevalue",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_text_node():
    node = TextNode("somevalue")

    expected = {
        "_type": "text",
        "value": "somevalue",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_verbatim_node():
    node = VerbatimNode("somevalue")

    expected = {
        "_type": "verbatim",
        "value": "somevalue",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_style_node_without_content():
    node = StyleNode("mystyle")

    expected = {
        "_type": "style",
        "style": "mystyle",
        "content": [],
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_style_node_with_content():
    node = StyleNode("mystyle")

    check_node_with_content(node)
