import pytest
from mau.nodes.footnotes import FootnoteNode
from mau.nodes.inline import (
    ClassNode,
    ImageNode,
    LinkNode,
    ListItemNode,
    MacroNode,
    SentenceNode,
    StyleNode,
    TextNode,
    VerbatimNode,
)
from mau.nodes.references import ReferenceNode
from mau.visitors.base_visitor import BaseVisitor, VisitorError


def test_no_node():
    visitor = BaseVisitor()

    result = visitor.visit(None)

    assert result == {}


def test_unknown_node():
    visitor = BaseVisitor()

    node = TextNode("Just some text.")
    node.node_type = "unknown"

    with pytest.raises(VisitorError):
        visitor.visit(node)


def test_text_node():
    visitor = BaseVisitor()

    node = TextNode("Just some text.")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "text",
            "value": "Just some text.",
        }
    }


def test_verbatim_node():
    visitor = BaseVisitor()

    node = VerbatimNode("Just some text.")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "verbatim",
            "value": "Just some text.",
        }
    }


def test_sentence_node():
    visitor = BaseVisitor()

    node = SentenceNode(
        [
            TextNode("Just some text. "),
            TextNode("More text."),
        ]
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "sentence",
            "content": [
                {
                    "data": {
                        "type": "text",
                        "value": "Just some text. ",
                    }
                },
                {
                    "data": {
                        "type": "text",
                        "value": "More text.",
                    }
                },
            ],
        }
    }


def test_style_node_star():
    visitor = BaseVisitor()

    node = StyleNode("star", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "style",
            "content": {
                "data": {
                    "type": "sentence",
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "Just some text.",
                            }
                        },
                    ],
                }
            },
            "value": "star",
        }
    }


def test_style_node_underscore():
    visitor = BaseVisitor()

    node = StyleNode("underscore", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "style",
            "content": {
                "data": {
                    "type": "sentence",
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "Just some text.",
                            }
                        },
                    ],
                }
            },
            "value": "underscore",
        }
    }


def test_style_node_tilde():
    visitor = BaseVisitor()

    node = StyleNode("tilde", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "style",
            "content": {
                "data": {
                    "type": "sentence",
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "Just some text.",
                            }
                        },
                    ],
                }
            },
            "value": "tilde",
        }
    }


def test_style_node_caret():
    visitor = BaseVisitor()

    node = StyleNode("caret", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "style",
            "content": {
                "data": {
                    "type": "sentence",
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "Just some text.",
                            }
                        },
                    ],
                }
            },
            "value": "caret",
        }
    }


def test_macro_node():
    visitor = BaseVisitor()

    node = MacroNode("somename", ["arg1", "arg2"], {"key1": "value1"})

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "macro",
            "name": "somename",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
        }
    }


def test_footnote_node():
    visitor = BaseVisitor()

    node = FootnoteNode(
        content=[TextNode("Just some text.")],
        number="5",
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "footnote",
            "number": "5",
            "reference_anchor": "someanchor",
            "content_anchor": "someanchor-def",
            "content": [
                {"data": {"type": "text", "value": "Just some text."}},
            ],
        }
    }


def test_reference_node():
    visitor = BaseVisitor()

    node = ReferenceNode(
        content_type="somecontent",
        name="somename",
        category="somecategory",
        content=[TextNode("Just some text.")],
        number="5",
        title=SentenceNode([TextNode("Some title")]),
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "reference",
            "category": "somecategory",
            "content_type": "somecontent",
            "name": "somename",
            "number": "5",
            "reference_anchor": "someanchor",
            "content_anchor": "someanchor-def",
            "content": [
                {
                    "data": {"type": "text", "value": "Just some text."},
                }
            ],
            "title": {
                "data": {
                    "type": "sentence",
                    "content": [
                        {
                            "data": {
                                "type": "text",
                                "value": "Some title",
                            },
                        }
                    ],
                }
            },
        }
    }


def test_class_node():
    visitor = BaseVisitor()

    node = ClassNode(["class1", "class2"], TextNode("Just some text."))

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "class",
            "content": {
                "data": {
                    "type": "text",
                    "value": "Just some text.",
                }
            },
            "classes": ["class1", "class2"],
        }
    }


def test_link_node():
    visitor = BaseVisitor()

    node = LinkNode(target="sometarget", text="sometext")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "link",
            "text": "sometext",
            "target": "sometarget",
        }
    }


def test_image_node():
    visitor = BaseVisitor()

    node = ImageNode(uri="someuri", alt_text="sometext", width="100", height="400")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "image",
            "uri": "someuri",
            "alt_text": "sometext",
            "width": "100",
            "height": "400",
        }
    }


def test_list_item_node():
    visitor = BaseVisitor()

    node = ListItemNode("4", TextNode("Just some text."))

    result = visitor.visit(node)

    assert result == {
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
