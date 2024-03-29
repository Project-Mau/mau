import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.nodes.footnotes import FootnoteNode
from mau.nodes.inline import RawNode, SentenceNode, StyleNode, TextNode, VerbatimNode
from mau.nodes.macros import MacroClassNode, MacroImageNode, MacroLinkNode, MacroNode
from mau.nodes.references import ReferenceNode
from mau.visitors.base_visitor import BaseVisitor


def test_no_node():
    visitor = BaseVisitor(Environment())

    result = visitor.visit(None)

    assert result == {}


def test_unknown_node():
    visitor = BaseVisitor(Environment())

    node = TextNode("Just some text.")
    node.node_type = "unknown"

    with pytest.raises(MauErrorException):
        visitor.visit(node)


def test_raw_node():
    visitor = BaseVisitor(Environment())

    node = RawNode("Just some text.")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "raw",
            "value": "Just some text.",
        }
    }


def test_text_node():
    visitor = BaseVisitor(Environment())

    node = TextNode("Just some text.")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "text",
            "value": "Just some text.",
        }
    }


def test_verbatim_node():
    visitor = BaseVisitor(Environment())

    node = VerbatimNode("Just some text.")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "verbatim",
            "value": "Just some text.",
        }
    }


def test_sentence_node():
    visitor = BaseVisitor(Environment())

    node = SentenceNode(
        children=[
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
    visitor = BaseVisitor(Environment())

    node = StyleNode("star", [TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "style",
            "content": [
                {
                    "data": {
                        "type": "text",
                        "value": "Just some text.",
                    }
                },
            ],
            "value": "star",
        }
    }


def test_style_node_underscore():
    visitor = BaseVisitor(Environment())

    node = StyleNode("underscore", [TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "style",
            "content": [
                {
                    "data": {
                        "type": "text",
                        "value": "Just some text.",
                    }
                },
            ],
            "value": "underscore",
        }
    }


def test_style_node_tilde():
    visitor = BaseVisitor(Environment())

    node = StyleNode("tilde", [TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "style",
            "content": [
                {
                    "data": {
                        "type": "text",
                        "value": "Just some text.",
                    }
                },
            ],
            "value": "tilde",
        }
    }


def test_style_node_caret():
    visitor = BaseVisitor(Environment())

    node = StyleNode("caret", [TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "style",
            "content": [
                {
                    "data": {
                        "type": "text",
                        "value": "Just some text.",
                    }
                },
            ],
            "value": "caret",
        }
    }


def test_macro_node():
    visitor = BaseVisitor(Environment())

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
    visitor = BaseVisitor(Environment())

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
    visitor = BaseVisitor(Environment())

    node = ReferenceNode(
        content_type="somecontent",
        content=[TextNode("Just some text.")],
        number="5",
        title=SentenceNode(children=[TextNode("Some title")]),
        reference_anchor="someanchor",
        content_anchor="someanchor-def",
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "reference",
            "content_type": "somecontent",
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
    visitor = BaseVisitor(Environment())

    node = MacroClassNode(["class1", "class2"], TextNode("Just some text."))

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "macro__class",
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
    visitor = BaseVisitor(Environment())

    node = MacroLinkNode(target="sometarget", text="sometext")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "macro__link",
            "text": "sometext",
            "target": "sometarget",
        }
    }


def test_image_node():
    visitor = BaseVisitor(Environment())

    node = MacroImageNode(uri="someuri", alt_text="sometext", width="100", height="400")

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "macro__image",
            "uri": "someuri",
            "alt_text": "sometext",
            "width": "100",
            "height": "400",
        }
    }
