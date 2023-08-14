from mau.nodes.footnotes import CommandFootnotesNode, FootnotesEntryNode
from mau.nodes.inline import ListItemNode, SentenceNode, TextNode
from mau.nodes.page import (
    BlockNode,
    CommandTocNode,
    ContentImageNode,
    ContentNode,
    DocumentNode,
    HeaderNode,
    HorizontalRuleNode,
    ListNode,
    ParagraphNode,
)
from mau.nodes.references import CommandReferencesNode, ReferencesEntryNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.visitors.base_visitor import BaseVisitor


def test_horizontal_rule_node():
    visitor = BaseVisitor()

    node = HorizontalRuleNode(
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "horizontal_rule",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_paragraph_node():
    visitor = BaseVisitor()

    node = ParagraphNode(
        TextNode("Just some text"),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "paragraph",
            "content": {
                "data": {
                    "type": "text",
                    "value": "Just some text",
                }
            },
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_header_node():
    visitor = BaseVisitor()

    node = HeaderNode(
        value="Just some text",
        level="3",
        anchor="someanchor",
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "header",
            "value": "Just some text",
            "level": 3,
            "anchor": "someanchor",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_list_node():
    visitor = BaseVisitor()

    node = ListNode(
        ordered=True,
        items=[ListItemNode("4", TextNode("Just some text."))],
        main_node=True,
        args=["arg1", "arg2"],
        kwargs={"key1": "value1", "start": 4},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "list",
            "items": [
                {
                    "data": {
                        "type": "list_item",
                        "level": 4,
                        "content": {
                            "data": {
                                "type": "text",
                                "value": "Just some text.",
                            }
                        },
                    }
                }
            ],
            "main_node": True,
            "ordered": True,
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1", "start": 4},
            "tags": ["tag1", "tag2"],
        }
    }


def test_content_node():
    visitor = BaseVisitor()

    node = ContentNode(
        content_type="sometype",
        title=TextNode("sometitle"),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "content",
            "content_type": "sometype",
            "title": {
                "data": {
                    "type": "text",
                    "value": "sometitle",
                }
            },
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_content_image_node():
    visitor = BaseVisitor()

    node = ContentImageNode(
        uri="someuri",
        alt_text="sometext",
        classes=["class1", "class2"],
        title=TextNode("sometitle"),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "content_image",
            "uri": "someuri",
            "title": {
                "data": {
                    "type": "text",
                    "value": "sometitle",
                }
            },
            "alt_text": "sometext",
            "classes": ["class1", "class2"],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_block_node_standard_block_template():
    visitor = BaseVisitor()

    node = BlockNode(
        blocktype="someblock",
        content=[TextNode("my content")],
        secondary_content=[TextNode("my secondary content")],
        classes=["class1", "class2"],
        title=TextNode("sometitle"),
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
            "blocktype": "someblock",
            "content": [
                {
                    "data": {
                        "type": "text",
                        "value": "my content",
                    }
                }
            ],
            "secondary_content": [
                {
                    "data": {
                        "type": "text",
                        "value": "my secondary content",
                    }
                }
            ],
            "classes": ["class1", "class2"],
            "title": {
                "data": {
                    "type": "text",
                    "value": "sometitle",
                }
            },
            "engine": "someengine",
            "preprocessor": "somepreprocessor",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_command_toc_node():
    visitor = BaseVisitor()

    node = CommandTocNode(
        entries=[
            HeaderNode("Header 1", "1", "header-1"),
            HeaderNode("Header 1.1", "2", "header-1-1"),
            HeaderNode("Header 2", "1", "header-2"),
        ],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "command_toc",
            "entries": [
                {
                    "data": {
                        "anchor": "header-1",
                        "args": ["arg1", "arg2"],
                        "children": [
                            {
                                "data": {
                                    "anchor": "header-1-1",
                                    "args": ["arg1", "arg2"],
                                    "children": [],
                                    "kwargs": {"key1": "value1"},
                                    "tags": ["tag1", "tag2"],
                                    "type": "toc_entry",
                                    "value": "Header 1.1",
                                }
                            },
                        ],
                        "kwargs": {"key1": "value1"},
                        "tags": ["tag1", "tag2"],
                        "type": "toc_entry",
                        "value": "Header 1",
                    }
                },
                {
                    "data": {
                        "type": "toc_entry",
                        "anchor": "header-2",
                        "args": ["arg1", "arg2"],
                        "children": [],
                        "kwargs": {"key1": "value1"},
                        "tags": ["tag1", "tag2"],
                        "value": "Header 2",
                    }
                },
            ],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_command_toc_node_exclude():
    visitor = BaseVisitor()

    node = CommandTocNode(
        entries=[
            HeaderNode("Header 1", "1", "header-1", tags=["notoc"]),
            HeaderNode("Header 1.1", "2", "header-1-1"),
            HeaderNode("Header 2", "1", "header-2"),
        ],
        args=["arg1", "arg2"],
        kwargs={"exclude_tag": "notoc"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "command_toc",
            "entries": [
                {
                    "data": {
                        "type": "toc_entry",
                        "anchor": "header-2",
                        "args": ["arg1", "arg2"],
                        "children": [],
                        "kwargs": {"exclude_tag": "notoc"},
                        "tags": ["tag1", "tag2"],
                        "value": "Header 2",
                    }
                },
            ],
            "args": ["arg1", "arg2"],
            "kwargs": {"exclude_tag": "notoc"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_command_footnotes_node():
    visitor = BaseVisitor()

    node = CommandFootnotesNode(
        entries=[
            FootnotesEntryNode(
                [TextNode("Footnote 1")], "1", "anchor-1", "anchor-1-def"
            ),
            FootnotesEntryNode(
                [TextNode("Footnote 2")], "2", "anchor-2", "anchor-2-def"
            ),
        ],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "command_footnotes",
            "entries": [
                {
                    "data": {
                        "content": [
                            {
                                "data": {
                                    "type": "text",
                                    "value": "Footnote 1",
                                }
                            },
                        ],
                        "content_anchor": "anchor-1-def",
                        "number": "1",
                        "reference_anchor": "anchor-1",
                        "type": "footnotes_entry",
                    }
                },
                {
                    "data": {
                        "content": [
                            {
                                "data": {
                                    "type": "text",
                                    "value": "Footnote 2",
                                }
                            },
                        ],
                        "content_anchor": "anchor-2-def",
                        "number": "2",
                        "reference_anchor": "anchor-2",
                        "type": "footnotes_entry",
                    }
                },
            ],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_command_references():
    visitor = BaseVisitor()

    node = CommandReferencesNode(
        content_type="content_type1",
        name="value1",
        category=None,
        entries={
            ("content_type1", "value1"): ReferencesEntryNode(
                "content_type1",
                "value1",
                content=[
                    ParagraphNode(
                        SentenceNode(
                            [
                                TextNode("Content type 1, value 1"),
                            ]
                        )
                    ),
                ],
                number=1,
                reference_anchor="ref-content_type1-1-XXYY",
                content_anchor="cnt-content_type1-1-XXYY",
            ),
            ("content_type1", "value2"): ReferencesEntryNode(
                "content_type1",
                "value2",
                content=[
                    ParagraphNode(
                        SentenceNode(
                            [
                                TextNode("Content type 1, value 2"),
                            ]
                        )
                    ),
                ],
                number=2,
                reference_anchor="ref-content_type1-2-XXYY",
                content_anchor="cnt-content_type1-2-XXYY",
            ),
            ("content_type2", "value1"): ReferencesEntryNode(
                "content_type2",
                "value1",
                content=[
                    ParagraphNode(
                        SentenceNode(
                            [
                                TextNode("Content type 2, value 1"),
                            ]
                        )
                    ),
                ],
                number=1,
                reference_anchor="ref-content_type2-1-XXYY",
                content_anchor="cnt-content_type2-1-XXYY",
            ),
        },
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "args": ["arg1", "arg2"],
            "content_type": "content_type1",
            "category": None,
            "entries": [
                {
                    "data": {
                        "category": None,
                        "content": [
                            {
                                "data": {
                                    "args": [],
                                    "content": {
                                        "data": {
                                            "content": [
                                                {
                                                    "data": {
                                                        "type": "text",
                                                        "value": "Content type 1, value 1",
                                                    }
                                                },
                                            ],
                                            "type": "sentence",
                                        }
                                    },
                                    "kwargs": {},
                                    "tags": [],
                                    "type": "paragraph",
                                }
                            },
                        ],
                        "content_anchor": "cnt-content_type1-1-XXYY",
                        "content_type": "content_type1",
                        "name": "value1",
                        "number": 1,
                        "reference_anchor": "ref-content_type1-1-XXYY",
                        "title": {},
                        "type": "references_entry",
                    }
                },
            ],
            "kwargs": {"key1": "value1"},
            "name": "value1",
            "tags": ["tag1", "tag2"],
            "type": "command_references",
        }
    }


def test_command_references_category():
    visitor = BaseVisitor()

    node = CommandReferencesNode(
        content_type="content_type1",
        name=None,
        category="cat1",
        entries={
            ("content_type1", "value1"): ReferencesEntryNode(
                "content_type1",
                "value1",
                category="cat1",
                content=[
                    ParagraphNode(
                        SentenceNode(
                            [
                                TextNode("Content type 1, value 1"),
                            ]
                        )
                    ),
                ],
                number=1,
                reference_anchor="ref-content_type1-1-XXYY",
                content_anchor="cnt-content_type1-1-XXYY",
            ),
            ("content_type1", "value2"): ReferencesEntryNode(
                "content_type1",
                "value2",
                category="cat2",
                content=[
                    ParagraphNode(
                        SentenceNode(
                            [
                                TextNode("Content type 1, value 2"),
                            ]
                        )
                    ),
                ],
                number=2,
                reference_anchor="ref-content_type1-2-XXYY",
                content_anchor="cnt-content_type1-2-XXYY",
            ),
            ("content_type1", "value3"): ReferencesEntryNode(
                "content_type1",
                "value3",
                category="cat1",
                content=[
                    ParagraphNode(
                        SentenceNode(
                            [
                                TextNode("Content type 1, value 3"),
                            ]
                        )
                    ),
                ],
                number=1,
                reference_anchor="ref-content_type1-3-XXYY",
                content_anchor="cnt-content_type1-3-XXYY",
            ),
        },
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "args": ["arg1", "arg2"],
            "content_type": "content_type1",
            "category": "cat1",
            "entries": [
                {
                    "data": {
                        "category": "cat1",
                        "content": [
                            {
                                "data": {
                                    "args": [],
                                    "content": {
                                        "data": {
                                            "content": [
                                                {
                                                    "data": {
                                                        "type": "text",
                                                        "value": "Content type 1, value 1",
                                                    }
                                                },
                                            ],
                                            "type": "sentence",
                                        }
                                    },
                                    "kwargs": {},
                                    "tags": [],
                                    "type": "paragraph",
                                }
                            },
                        ],
                        "content_anchor": "cnt-content_type1-1-XXYY",
                        "content_type": "content_type1",
                        "name": "value1",
                        "number": 1,
                        "reference_anchor": "ref-content_type1-1-XXYY",
                        "title": {},
                        "type": "references_entry",
                    }
                },
                {
                    "data": {
                        "category": "cat1",
                        "content": [
                            {
                                "data": {
                                    "args": [],
                                    "content": {
                                        "data": {
                                            "content": [
                                                {
                                                    "data": {
                                                        "type": "text",
                                                        "value": "Content type 1, value 3",
                                                    }
                                                },
                                            ],
                                            "type": "sentence",
                                        }
                                    },
                                    "kwargs": {},
                                    "tags": [],
                                    "type": "paragraph",
                                }
                            },
                        ],
                        "content_anchor": "cnt-content_type1-3-XXYY",
                        "content_type": "content_type1",
                        "name": "value3",
                        "number": 1,
                        "reference_anchor": "ref-content_type1-3-XXYY",
                        "title": {},
                        "type": "references_entry",
                    }
                },
            ],
            "kwargs": {"key1": "value1"},
            "name": None,
            "tags": ["tag1", "tag2"],
            "type": "command_references",
        }
    }


def test_source_node():
    visitor = BaseVisitor()

    node = SourceNode(
        language="somelang",
        code=[
            TextNode("import sys"),
            TextNode("import: os"),
            TextNode(""),
            TextNode('print(os.environ["HOME"])'),
        ],
        markers=[CalloutNode(1, "imp"), CalloutNode(3, "env")],
        callouts=[
            CalloutsEntryNode("imp", "This is an import"),
            CalloutsEntryNode("env", "Environment variables are paramount"),
        ],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "source",
            "blocktype": "default",
            "callouts": [
                {
                    "data": {
                        "marker": "imp",
                        "type": "callouts_entry",
                        "value": "This is an import",
                    }
                },
                {
                    "data": {
                        "marker": "env",
                        "type": "callouts_entry",
                        "value": "Environment variables are paramount",
                    }
                },
            ],
            "classes": [],
            "code": [
                {"data": {"type": "text", "value": "import sys"}},
                {"data": {"type": "text", "value": "import: os"}},
                {"data": {"type": "text", "value": ""}},
                {
                    "data": {
                        "type": "text",
                        "value": 'print(os.environ["HOME"])',
                    }
                },
            ],
            "highlights": [],
            "language": "somelang",
            "lines": 4,
            "markers": [
                None,
                {"data": {"type": "callout", "line": 1, "marker": "imp"}},
                None,
                {"data": {"type": "callout", "line": 3, "marker": "env"}},
            ],
            "preprocessor": None,
            "title": {},
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_document_node():
    visitor = BaseVisitor()

    node = DocumentNode(
        content=[
            ParagraphNode(
                TextNode("Just some text"),
                args=["arg1", "arg2"],
                kwargs={"key1": "value1"},
                tags=["tag1", "tag2"],
            )
        ],
        args=["arg3", "arg4"],
        kwargs={"key2": "value2"},
        tags=["tag3", "tag4"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "document",
            "content": [
                {
                    "data": {
                        "type": "paragraph",
                        "content": {
                            "data": {
                                "type": "text",
                                "value": "Just some text",
                            }
                        },
                        "args": ["arg1", "arg2"],
                        "kwargs": {"key1": "value1"},
                        "tags": ["tag1", "tag2"],
                    }
                }
            ],
            "args": ["arg3", "arg4"],
            "kwargs": {"key2": "value2"},
            "tags": ["tag3", "tag4"],
        }
    }
