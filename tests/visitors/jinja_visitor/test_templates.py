from mau.environment.environment import Environment
from mau.nodes.inline import TextNode
from mau.nodes.nodes import Node
from mau.nodes.paragraph import ParagraphNode
from mau.visitors.jinja_visitor import JinjaVisitor, create_templates


def test_create_templates_prefixes():
    child_node = Node()
    child_node.node_type = "node_type"

    parent_node = Node()
    parent_node.node_type = "parent_type"

    child_node.parent = parent_node
    parent_node.children.append(child_node)

    templates = create_templates(
        ["prefix1", "prefix2"], ["node_template1"], child_node, "ext"
    )

    assert templates == [
        "prefix1.parent_type.node_template1.ext",
        "prefix1.parent_type.node_type.ext",
        "prefix1.node_template1.ext",
        "prefix1.node_type.ext",
        "prefix2.parent_type.node_template1.ext",
        "prefix2.parent_type.node_type.ext",
        "prefix2.node_template1.ext",
        "prefix2.node_type.ext",
        "parent_type.node_template1.ext",
        "parent_type.node_type.ext",
        "node_template1.ext",
        "node_type.ext",
    ]


def test_create_templates_node_subtype():
    child_node = Node()
    child_node.node_type = "node_type"
    child_node.subtype = "node_subtype"

    parent_node = Node()
    parent_node.node_type = "parent_type"

    child_node.parent = parent_node
    parent_node.children.append(child_node)

    templates = create_templates([], ["node_template1"], child_node, "ext")

    assert templates == [
        "parent_type.node_template1.node_subtype.ext",
        "parent_type.node_template1.ext",
        "parent_type.node_type.node_subtype.ext",
        "parent_type.node_type.ext",
        "node_template1.node_subtype.ext",
        "node_template1.ext",
        "node_type.node_subtype.ext",
        "node_type.ext",
    ]


def test_create_templates_node_templates():
    child_node = Node()
    child_node.node_type = "node_type"

    parent_node = Node()
    parent_node.node_type = "parent_type"

    child_node.parent = parent_node
    parent_node.children.append(child_node)

    templates = create_templates(
        [], ["node_template1", "node_template2"], child_node, "ext"
    )

    assert templates == [
        "parent_type.node_template1.ext",
        "parent_type.node_template2.ext",
        "parent_type.node_type.ext",
        "node_template1.ext",
        "node_template2.ext",
        "node_type.ext",
    ]


def test_create_templates_parent_subtype():
    child_node = Node()
    child_node.node_type = "node_type"

    parent_node = Node()
    parent_node.node_type = "parent_type"
    parent_node.subtype = "parent_subtype"

    child_node.parent = parent_node
    parent_node.children.append(child_node)

    templates = create_templates([], ["node_template1"], child_node, "ext")

    assert templates == [
        "parent_type.parent_subtype.node_template1.ext",
        "parent_type.parent_subtype.node_type.ext",
        "parent_type.node_template1.ext",
        "parent_type.node_type.ext",
        "node_template1.ext",
        "node_type.ext",
    ]


def test_create_templates_parent_position():
    child_node = Node()
    child_node.node_type = "node_type"

    parent_node = Node()
    parent_node.node_type = "parent_type"
    parent_node.subtype = "parent_subtype"

    child_node.parent = parent_node
    child_node.parent_position = "primary"
    parent_node.children.append(child_node)

    templates = create_templates([], ["node_template1"], child_node, "ext")

    assert templates == [
        "parent_type.parent_subtype.primary.node_template1.ext",
        "parent_type.parent_subtype.primary.node_type.ext",
        "parent_type.parent_subtype.node_template1.ext",
        "parent_type.parent_subtype.node_type.ext",
        "parent_type.primary.node_template1.ext",
        "parent_type.primary.node_type.ext",
        "parent_type.node_template1.ext",
        "parent_type.node_type.ext",
        "node_template1.ext",
        "node_type.ext",
    ]


def test_create_templates():
    child_node = Node()
    child_node.node_type = "node_type"
    child_node.subtype = "node_subtype"
    child_node.tags = ["tag1", "tag2"]

    templates = create_templates([], ["node_template1"], child_node, "ext")

    assert templates == [
        "node_template1.node_subtype.tag1.ext",
        "node_template1.node_subtype.tag2.ext",
        "node_template1.node_subtype.ext",
        "node_template1.tag1.ext",
        "node_template1.tag2.ext",
        "node_template1.ext",
        "node_type.node_subtype.tag1.ext",
        "node_type.node_subtype.tag2.ext",
        "node_type.node_subtype.ext",
        "node_type.tag1.ext",
        "node_type.tag2.ext",
        "node_type.ext",
    ]


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
