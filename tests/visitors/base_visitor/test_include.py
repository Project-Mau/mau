from mau.nodes.block import BlockNode
from mau.nodes.footnote import FootnoteNode
from mau.nodes.header import HeaderNode
from mau.nodes.include import (
    BlockGroupItemNode,
    BlockGroupNode,
    FootnotesItemNode,
    FootnotesNode,
    IncludeImageNode,
    IncludeNode,
    TocItemNode,
    TocNode,
)
from mau.test_helpers import check_visit_node


def test_include_node():
    node = IncludeNode("ctype")

    expected = {
        "_type": "include",
        "ctype": "ctype",
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_include_image_node():
    node = IncludeImageNode("uri")

    expected = {
        "_type": "include-image",
        "uri": "uri",
        "alt_text": None,
        "classes": [],
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_include_image_node_alt_text_classes():
    node = IncludeImageNode("uri", "alt_text", ["class1", "class2"])

    expected = {
        "_type": "include-image",
        "uri": "uri",
        "alt_text": "alt_text",
        "classes": ["class1", "class2"],
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_footnotes_node_empty():
    node = FootnotesNode()

    expected = {
        "_type": "footnotes",
        "footnotes": [],
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_footnotes_node():
    footnotes_items = [
        FootnotesItemNode(footnote=FootnoteNode("somename1")),
        FootnotesItemNode(footnote=FootnoteNode("somename2")),
    ]

    node = FootnotesNode(footnotes=footnotes_items)

    expected = {
        "_type": "footnotes",
        "footnotes": [
            {
                "_type": "footnotes-item",
                "footnote": {
                    "_type": "footnote",
                    "content": [],
                    "internal_id": None,
                    "name": "somename1",
                    "kwargs": {},
                    "public_id": None,
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
            },
            {
                "_type": "footnotes-item",
                "footnote": {
                    "_type": "footnote",
                    "content": [],
                    "internal_id": None,
                    "name": "somename2",
                    "kwargs": {},
                    "public_id": None,
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
            },
        ],
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_toc_item_node_without_entries():
    node = TocItemNode(
        header=HeaderNode(level=1),
        entries=[],
    )

    expected = {
        "_type": "toc-item",
        "entries": [],
        "header": {
            "_type": "header",
            "level": 1,
            "internal_id": None,
            "name": None,
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


def test_toc_item_node_with_entries():
    toc_item_child = TocItemNode(
        header=HeaderNode(level=2),
        entries=[],
    )

    node = TocItemNode(
        header=HeaderNode(level=1),
        entries=[toc_item_child],
    )

    expected = {
        "_type": "toc-item",
        "entries": [
            {
                "_type": "toc-item",
                "entries": [],
                "header": {
                    "_type": "header",
                    "level": 2,
                    "internal_id": None,
                    "name": None,
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
        ],
        "header": {
            "_type": "header",
            "level": 1,
            "internal_id": None,
            "name": None,
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


def test_toc_node():
    node = TocNode()

    expected = {
        "_type": "toc",
        "plain_entries": [],
        "nested_entries": [],
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_block_group_node_empty():
    node = BlockGroupNode("somename")

    expected = {
        "_type": "blockgroup",
        "name": "somename",
        "items": {},
        "labels": {},
        "kwargs": {},
        "subtype": None,
        "tags": [],
        "internal_tags": [],
        "args": [],
    }

    check_visit_node(node, expected)


def test_block_group_node_with_blocks():
    block_node1 = BlockNode()
    block_node2 = BlockNode()

    node = BlockGroupNode("somename")

    blockgroup_item_node1 = BlockGroupItemNode(
        "somename",
        "position1",
        block_node1,
    )
    blockgroup_item_node2 = BlockGroupItemNode(
        "somename",
        "position2",
        block_node2,
    )

    node.items = {
        "position1": blockgroup_item_node1,
        "position2": blockgroup_item_node2,
    }

    expected = {
        "_type": "blockgroup",
        "name": "somename",
        "labels": {},
        "items": {
            "position1": {
                "_type": "blockgroup-item",
                "block": {
                    "_type": "block",
                    "classes": [],
                    "content": [],
                    "labels": {},
                    "kwargs": {},
                    "subtype": None,
                    "tags": [],
                    "internal_tags": [],
                    "args": [],
                },
                "block_data": {
                    "_type": "block",
                    "classes": [],
                    "content": [],
                    "labels": {},
                    "kwargs": {},
                    "subtype": None,
                    "tags": [],
                    "internal_tags": [],
                    "args": [],
                },
                "kwargs": {},
                "position": "position1",
                "subtype": None,
                "tags": [],
                "internal_tags": [],
                "args": [],
            },
            "position2": {
                "_type": "blockgroup-item",
                "block": {
                    "_type": "block",
                    "classes": [],
                    "content": [],
                    "labels": {},
                    "kwargs": {},
                    "subtype": None,
                    "tags": [],
                    "internal_tags": [],
                    "args": [],
                },
                "block_data": {
                    "_type": "block",
                    "classes": [],
                    "content": [],
                    "labels": {},
                    "kwargs": {},
                    "subtype": None,
                    "tags": [],
                    "internal_tags": [],
                    "args": [],
                },
                "kwargs": {},
                "position": "position2",
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
