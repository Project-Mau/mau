import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
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
from mau.visitors.jinja_visitor import JinjaVisitor


def test_default_values():
    visitor = JinjaVisitor(Environment())

    assert visitor.default_templates == Environment()
    assert visitor.environment_options == {}
    assert visitor.extension == "j2"
    assert visitor.toc is None
    assert visitor.footnotes is None

    assert visitor.templates == Environment()


def test_custom_templates():
    templates = {"key": "value"}

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")

    visitor = JinjaVisitor(environment)

    assert visitor.templates.asdict() == templates


def test_custom_templates_with_default_templates():
    class MyJinjaVisitor(JinjaVisitor):
        default_templates = {"defaultkey": "defaultvalue"}

    templates = {"key": "value"}
    merged_templates = Environment({"defaultkey": "defaultvalue", "key": "value"})

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")

    visitor = MyJinjaVisitor(environment)

    assert visitor.templates == merged_templates


def test_no_templates():
    templates = {}

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = TextNode("Just some text.")

    with pytest.raises(MauErrorException):
        visitor.visit(node)


def test_inline_text_node():
    templates = {
        "text.j2": "{{ value }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = TextNode("Just some text.")

    result = visitor.visit(node)

    assert result == "Just some text."


def test_inline_text_node_with_no_prefix():
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


def test_inline_verbatim_node():
    templates = {
        "verbatim.j2": "{{ value }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = VerbatimNode("Just some text.")

    result = visitor.visit(node)

    assert result == "Just some text."


def test_inline_sentence_node():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = SentenceNode(
        [
            TextNode("Just some text. "),
            TextNode("More text."),
        ]
    )

    result = visitor.visit(node)

    assert result == "Just some text. More text."


def test_inline_style_node_star():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "style.star.j2": "*{{ content }}*",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = StyleNode("star", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == "*Just some text.*"


def test_inline_style_node_underscore():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "style.underscore.j2": "_{{ content }}_",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = StyleNode("underscore", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == "_Just some text._"


def test_inline_style_node_tilde():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "style.tilde.j2": "~{{ content }}~",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = StyleNode("tilde", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == "~Just some text.~"


def test_inline_style_node_caret():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "style.caret.j2": "^{{ content }}^",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = StyleNode("caret", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == "^Just some text.^"


def test_inline_macro_node():
    templates = {
        "text.j2": "{{ value }}",
        "macro.j2": (
            "{{ name }} - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = MacroNode("somename", ["arg1", "arg2"], {"key1": "value1"})

    result = visitor.visit(node)

    assert result == "somename - arg1,arg2 - key1:value1"


def test_inline_footnote_node():
    templates = {
        "text.j2": "{{ value }}",
        "footnote.j2": (
            "{{ content }} - {{ number }} - "
            "{{ reference_anchor }} - {{ content_anchor }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = FootnoteNode(
        [TextNode("Just some text.")], "5", "someanchor", "someanchor-def"
    )

    result = visitor.visit(node)

    assert result == "Just some text. - 5 - someanchor - someanchor-def"


def test_inline_reference_node():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "reference.somecontent.j2": (
            "{{ content_type }} - {{ content }} - "
            "{{ number }} - {{ title }} - {{ reference_anchor }} - {{ content_anchor }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = ReferenceNode(
        "somecontent",
        [TextNode("Just some text.")],
        "5",
        SentenceNode([TextNode("Some title")]),
        "someanchor",
        "someanchor-def",
    )

    result = visitor.visit(node)

    assert result == (
        "somecontent - Just some text. "
        "- 5 - Some title - someanchor - someanchor-def"
    )


def test_inline_class_node():
    templates = {
        "text.j2": "{{ value }}",
        "class.j2": "{{ classes | join(',') }} - {{ content }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = ClassNode(["class1", "class2"], TextNode("Just some text."))

    result = visitor.visit(node)

    assert result == "class1,class2 - Just some text."


def test_inline_link_node():
    templates = {
        "text.j2": "{{ value }}",
        "link.j2": "{{ target }} - {{ text }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = LinkNode(target="sometarget", text="sometext")

    result = visitor.visit(node)

    assert result == "sometarget - sometext"


def test_inline_image_node():
    templates = {
        "text.j2": "{{ value }}",
        "image.j2": "{{ uri }} - {{ alt_text }} - {{ width }}x{{ height }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = ImageNode(uri="someuri", alt_text="sometext", width="100", height="400")

    result = visitor.visit(node)

    assert result == "someuri - sometext - 100x400"


def test_inline_list_item_node():
    templates = {
        "text.j2": "{{ value }}",
        "list_item.j2": "{{ level }} - {{ content }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = ListItemNode("4", TextNode("Just some text."))

    result = visitor.visit(node)

    assert result == "4 - Just some text."
