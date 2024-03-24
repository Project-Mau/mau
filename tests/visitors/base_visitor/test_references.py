from mau.environment.environment import Environment
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.references import ReferencesEntryNode, ReferencesNode
from mau.visitors.base_visitor import BaseVisitor


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