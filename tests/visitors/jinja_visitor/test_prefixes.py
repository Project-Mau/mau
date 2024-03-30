import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.nodes.footnotes import FootnoteNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.inline import SentenceNode, StyleNode, TextNode, VerbatimNode
from mau.nodes.macros import MacroClassNode, MacroImageNode, MacroLinkNode, MacroNode
from mau.nodes.references import ReferenceNode
from mau.visitors.jinja_visitor import JinjaVisitor


def test_inline_text_node_without_prefix():
    templates = {
        "text.j2": "{{ value }}",
        "prefix.text.j2": "PREFIXED {{ value }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    environment.setvar("mau.visitor.prefixes", [])
    visitor = JinjaVisitor(environment)

    node = TextNode("Just some text.")

    result = visitor.visit(node)

    assert result == "Just some text."


def test_inline_text_node_with_prefix():
    templates = {
        "text.j2": "{{ value }}",
        "prefix.text.j2": "PREFIXED {{ value }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    environment.setvar("mau.visitor.prefixes", ["prefix"])
    visitor = JinjaVisitor(environment)

    node = TextNode("Just some text.")

    result = visitor.visit(node)

    assert result == "PREFIXED Just some text."


def test_inline_text_node_with_multiple_prefixes():
    templates = {
        "text.j2": "{{ value }}",
        "otherprefix.text.j2": "PREFIXED OTHER {{ value }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    environment.setvar("mau.visitor.prefixes", ["prefix", "otherprefix"])
    visitor = JinjaVisitor(environment)

    node = TextNode("Just some text.")

    result = visitor.visit(node)

    assert result == "PREFIXED OTHER Just some text."


def test_inline_text_node_with_parent():
    templates = {
        "text.j2": "{{ value }}",
        "paragraph.text.j2": "PARAGRAPH {{ value }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    text_node = TextNode("Just some text.")
    paragraph_node = ParagraphNode()
    text_node.parent = paragraph_node
    paragraph_node.children = [text_node]

    result = visitor.visit(text_node)

    assert result == "PARAGRAPH Just some text."


def test_inline_text_node_with_parent_subtype():
    templates = {
        "text.j2": "{{ value }}",
        "paragraph.text.j2": "PARAGRAPH {{ value }}",
        "paragraph.fancy.text.j2": "FANCY PARAGRAPH {{ value }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    text_node = TextNode("Just some text.")
    paragraph_node = ParagraphNode(subtype="fancy")
    text_node.parent = paragraph_node
    paragraph_node.children = [text_node]

    result = visitor.visit(text_node)

    assert result == "FANCY PARAGRAPH Just some text."
