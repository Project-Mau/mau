from mau.nodes.footnote import FootnoteNode
from mau.nodes.header import HeaderNode
from mau.nodes.macro import (
    MacroClassNode,
    MacroFootnoteNode,
    MacroHeaderNode,
    MacroImageNode,
    MacroLinkNode,
    MacroNode,
    MacroRawNode,
    MacroUnicodeNode,
)
from mau.nodes.node_arguments import NodeArguments
from mau.test_helpers import check_node_with_content, check_visit_node


def test_macro_node():
    node = MacroNode("somename")

    expected = {
        "_type": "macro",
        "name": "somename",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_macro_node_args():
    node = MacroNode(
        "somename",
        arguments=NodeArguments(
            unnamed_args=["arg1"],
            named_args={"key1": "value1"},
            tags=["tag1"],
            subtype="subtype1",
        ),
    )

    expected = {
        "_type": "macro",
        "name": "somename",
        "subtype": "subtype1",
        "tags": ["tag1"],
        "internal_tags": [],
        "args": ["arg1"],
        "kwargs": {"key1": "value1"},
    }

    check_visit_node(node, expected)


def test_macro_class_node_without_content():
    node = MacroClassNode(["class1", "class2"])

    expected = {
        "_type": "macro-class",
        "classes": ["class1", "class2"],
        "content": [],
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_macro_class_node_with_content():
    node = MacroClassNode(["class1", "class2"])
    check_node_with_content(node)


def test_macro_link_node_without_content():
    node = MacroLinkNode("sometarget")

    expected = {
        "_type": "macro-link",
        "target": "sometarget",
        "content": [],
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_macro_link_node_with_content():
    node = MacroLinkNode("sometarget")
    check_node_with_content(node)


def test_macro_image_node():
    node = MacroImageNode("someuri")

    expected = {
        "_type": "macro-image",
        "uri": "someuri",
        "alt_text": None,
        "width": None,
        "height": None,
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_macro_image_node_parameters():
    node = MacroImageNode("someuri", "alt_text", "width", "height")

    expected = {
        "_type": "macro-image",
        "uri": "someuri",
        "alt_text": "alt_text",
        "width": "width",
        "height": "height",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_macro_header_node():
    node = MacroHeaderNode("someid")

    expected = {
        "_type": "macro-header",
        "target_name": "someid",
        "content": [],
        "header": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_macro_header_node_with_header():
    node = MacroHeaderNode("someid", header=HeaderNode(level=1))

    expected = {
        "_type": "macro-header",
        "target_name": "someid",
        "content": [],
        "header": {
            "_type": "header",
            "name": None,
            "internal_id": None,
            "level": 1,
            "labels": {},
            "content": [],
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


def test_macro_header_node_parameters():
    node = MacroHeaderNode(target_name="somename")

    expected = {
        "_type": "macro-header",
        "target_name": "somename",
        "content": [],
        "header": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_macro_footnote_node_parameters():
    node = MacroFootnoteNode(name="somename", footnote=FootnoteNode(name="somename"))

    expected = {
        "_type": "macro-footnote",
        "footnote": {
            "_type": "footnote",
            "name": "somename",
            "public_id": None,
            "internal_id": None,
            "content": [],
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


def test_macro_unicode():
    node = MacroUnicodeNode("1F30B")

    expected = {
        "_type": "macro-unicode",
        "value": "1F30B",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_macro_raw():
    node = MacroRawNode("somevalue")

    expected = {
        "_type": "macro-raw",
        "value": "somevalue",
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)
