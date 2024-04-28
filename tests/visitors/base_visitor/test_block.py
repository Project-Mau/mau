from mau.environment.environment import Environment
from mau.nodes.block import BlockGroupNode, BlockNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.visitors.base_visitor import BaseVisitor


def test_block_node_standard_block_template():
    visitor = BaseVisitor(Environment())

    node = BlockNode(
        subtype="someblock",
        children=[
            ParagraphNode(
                children=[
                    TextNode("my content"),
                ]
            ),
        ],
        secondary_children=[
            ParagraphNode(
                children=[
                    TextNode("my secondary content"),
                ]
            ),
        ],
        classes=["class1", "class2"],
        title=SentenceNode(children=[TextNode("sometitle")]),
        engine="someengine",
        preprocessor="somepreprocessor",
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "block",
            "subtype": "someblock",
            "content": [
                {
                    "data": {
                        "type": "paragraph",
                        "content": [
                            {
                                "data": {
                                    "type": "text",
                                    "value": "my content",
                                    "args": [],
                                    "kwargs": {},
                                    "subtype": None,
                                    "tags": [],
                                }
                            }
                        ],
                        "title": {},
                        "args": [],
                        "kwargs": {},
                        "subtype": None,
                        "tags": [],
                    }
                }
            ],
            "secondary_content": [
                {
                    "data": {
                        "type": "paragraph",
                        "content": [
                            {
                                "data": {
                                    "type": "text",
                                    "value": "my secondary content",
                                    "args": [],
                                    "kwargs": {},
                                    "subtype": None,
                                    "tags": [],
                                }
                            }
                        ],
                        "title": {},
                        "args": [],
                        "kwargs": {},
                        "subtype": None,
                        "tags": [],
                    }
                }
            ],
            "classes": ["class1", "class2"],
            "title": {
                "data": {
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "sometitle",
                                "args": [],
                                "kwargs": {},
                                "subtype": None,
                                "tags": [],
                            }
                        },
                    ],
                    "type": "sentence",
                    "args": [],
                    "kwargs": {},
                    "subtype": None,
                    "tags": [],
                },
            },
            "engine": "someengine",
            "preprocessor": "somepreprocessor",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_block_group():
    visitor = BaseVisitor(Environment())

    node = BlockGroupNode(
        group_name="somegroup",
        group={
            "left": BlockNode(
                subtype="sometype1",
                children=[
                    ParagraphNode(
                        children=[
                            TextNode("Block 1"),
                        ]
                    ),
                ],
                secondary_children=[],
                classes=[],
                title=None,
                engine="group",
                preprocessor="none",
                args=[],
                kwargs={},
            ),
            "right": BlockNode(
                subtype="sometype2",
                children=[
                    ParagraphNode(
                        children=[
                            TextNode("Block 2"),
                        ]
                    ),
                ],
                secondary_children=[],
                classes=[],
                title=None,
                engine="group",
                preprocessor="none",
                args=[],
                kwargs={},
            ),
        },
        args=[],
        kwargs={},
        tags=[],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "block_group",
            "group_name": "somegroup",
            "group": {
                "left": {
                    "data": {
                        "type": "block",
                        "subtype": "sometype1",
                        "content": [
                            {
                                "data": {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "data": {
                                                "type": "text",
                                                "value": "Block 1",
                                                "args": [],
                                                "kwargs": {},
                                                "subtype": None,
                                                "tags": [],
                                            }
                                        }
                                    ],
                                    "title": {},
                                    "args": [],
                                    "kwargs": {},
                                    "subtype": None,
                                    "tags": [],
                                }
                            }
                        ],
                        "secondary_content": [],
                        "classes": [],
                        "title": {},
                        "engine": "group",
                        "preprocessor": "none",
                        "args": [],
                        "kwargs": {},
                        "tags": [],
                    },
                },
                "right": {
                    "data": {
                        "type": "block",
                        "subtype": "sometype2",
                        "content": [
                            {
                                "data": {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "data": {
                                                "type": "text",
                                                "value": "Block 2",
                                                "args": [],
                                                "kwargs": {},
                                                "subtype": None,
                                                "tags": [],
                                            }
                                        }
                                    ],
                                    "title": {},
                                    "args": [],
                                    "kwargs": {},
                                    "subtype": None,
                                    "tags": [],
                                }
                            }
                        ],
                        "secondary_content": [],
                        "classes": [],
                        "title": {},
                        "engine": "group",
                        "preprocessor": "none",
                        "args": [],
                        "kwargs": {},
                        "tags": [],
                    },
                },
            },
            "title": {},
            "args": [],
            "kwargs": {},
            "tags": [],
            "subtype": None,
        }
    }
