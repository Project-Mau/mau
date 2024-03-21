from mau.environment.environment import Environment
from mau.nodes.footnotes import FootnoteNode, FootnotesNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import (
    BlockNode,
    ContentImageNode,
    ContentNode,
    DocumentNode,
    HeaderNode,
    HorizontalRuleNode,
    ParagraphNode,
)
from mau.nodes.references import ReferencesEntryNode, ReferencesNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.nodes.toc import TocEntryNode, TocNode
from mau.visitors.base_visitor import BaseVisitor


def test_horizontal_rule_node():
    visitor = BaseVisitor(Environment())

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
    visitor = BaseVisitor(Environment())

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
    visitor = BaseVisitor(Environment())

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


def test_content_node():
    visitor = BaseVisitor(Environment())

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
    visitor = BaseVisitor(Environment())

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
    visitor = BaseVisitor(Environment())

    node = BlockNode(
        subtype="someblock",
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
            "subtype": "someblock",
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


def test_toc_node():
    visitor = BaseVisitor(Environment())

    node = TocNode(
        entries=[
            TocEntryNode(
                "Header 1",
                "header-1",
                children=[
                    TocEntryNode("Header 1.1", "header-1-1"),
                ],
            ),
            TocEntryNode("Header 2", "header-2"),
        ],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "toc",
            "entries": [
                {
                    "data": {
                        "anchor": "header-1",
                        "args": [],
                        "children": [
                            {
                                "data": {
                                    "anchor": "header-1-1",
                                    "args": [],
                                    "children": [],
                                    "kwargs": {},
                                    "tags": [],
                                    "type": "toc_entry",
                                    "value": "Header 1.1",
                                }
                            },
                        ],
                        "kwargs": {},
                        "tags": [],
                        "type": "toc_entry",
                        "value": "Header 1",
                    }
                },
                {
                    "data": {
                        "type": "toc_entry",
                        "anchor": "header-2",
                        "args": [],
                        "children": [],
                        "kwargs": {},
                        "tags": [],
                        "value": "Header 2",
                    }
                },
            ],
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }


def test_footnotes_node():
    visitor = BaseVisitor(Environment())

    node = FootnotesNode(
        entries=[
            FootnoteNode(
                [TextNode("Footnote 1")], "1", "anchor-1", "anchor-1-def"
            ).to_entry(),
            FootnoteNode(
                [TextNode("Footnote 2")], "2", "anchor-2", "anchor-2-def"
            ).to_entry(),
        ],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "footnotes",
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


def test_references():
    visitor = BaseVisitor(Environment())

    node = ReferencesNode(
        content_type=None,
        entries=[
            ReferencesEntryNode(
                "content_type1",
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
            ReferencesEntryNode(
                "content_type2",
                content=[
                    ParagraphNode(
                        SentenceNode(
                            [
                                TextNode("Content type 2, value 1"),
                            ]
                        )
                    ),
                ],
                number=2,
                reference_anchor="ref-content_type2-2-XXYY",
                content_anchor="cnt-content_type2-2-XXYY",
            ),
        ],
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "args": ["arg1", "arg2"],
            "content_type": None,
            "entries": [
                {
                    "data": {
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
                        "number": 1,
                        "reference_anchor": "ref-content_type1-1-XXYY",
                        "title": {},
                        "type": "references_entry",
                    }
                },
                {
                    "data": {
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
                                                        "value": "Content type 2, value 1",
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
                        "content_anchor": "cnt-content_type2-2-XXYY",
                        "content_type": "content_type2",
                        "number": 2,
                        "reference_anchor": "ref-content_type2-2-XXYY",
                        "title": {},
                        "type": "references_entry",
                    }
                },
            ],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
            "type": "references",
        }
    }


def test_source_node():
    visitor = BaseVisitor(Environment())

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
            "subtype": "default",
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
    visitor = BaseVisitor(Environment())

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
