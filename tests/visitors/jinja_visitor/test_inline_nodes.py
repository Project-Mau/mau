import pytest

from mau.nodes.inline import (
    TextNode,
    VerbatimNode,
    SentenceNode,
    StyleNode,
    MacroNode,
    ClassNode,
    LinkNode,
    ImageNode,
    ListItemNode,
)

from mau.visitors.base_visitor import VisitorError
from mau.visitors.jinja_visitor import JinjaVisitor
from mau.nodes.footnotes import FootnoteNode
from mau.nodes.references import ReferenceNode


def test_default_values():
    visitor = JinjaVisitor()

    assert visitor.default_templates == {}
    assert visitor.environment_options == {}
    assert visitor.templates_directory is None
    assert visitor.config == {}
    assert visitor.extension == "j2"
    assert visitor.toc is None
    assert visitor.footnotes is None

    assert visitor.templates == {}


def test_custom_templates():
    sometemplates = {"key": "value"}
    visitor = JinjaVisitor(custom_templates=sometemplates)

    assert visitor.templates == sometemplates


def test_custom_templates_with_default_templates():
    class MyJinjaVisitor(JinjaVisitor):
        default_templates = {"defaultkey": "defaultvalue"}

    some_templates = {"key": "value"}
    merged_templates = {"defaultkey": "defaultvalue", "key": "value"}

    visitor = MyJinjaVisitor(custom_templates=some_templates)

    assert visitor.templates == merged_templates


def test_no_templates():
    templates = {}

    visitor = JinjaVisitor(custom_templates=templates)

    node = TextNode("Just some text.")

    with pytest.raises(VisitorError):
        visitor.visit(node)


def test_inline_text_node():
    templates = {
        "text.j2": "{{ value }}",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = TextNode("Just some text.")

    result = visitor.visit(node)

    assert result == "Just some text."


def test_inline_verbatim_node():
    templates = {
        "verbatim.j2": "{{ value }}",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = VerbatimNode("Just some text.")

    result = visitor.visit(node)

    assert result == "Just some text."


def test_inline_sentence_node():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
    }

    visitor = JinjaVisitor(custom_templates=templates)

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
        "star.j2": "*{{ content }}*",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = StyleNode("star", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == "*Just some text.*"


def test_inline_style_node_underscore():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "underscore.j2": "_{{ content }}_",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = StyleNode("underscore", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == "_Just some text._"


def test_inline_style_node_tilde():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "tilde.j2": "~{{ content }}~",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = StyleNode("tilde", SentenceNode([TextNode("Just some text.")]))

    result = visitor.visit(node)

    assert result == "~Just some text.~"


def test_inline_style_node_caret():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "caret.j2": "^{{ content }}^",
    }

    visitor = JinjaVisitor(custom_templates=templates)

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

    visitor = JinjaVisitor(custom_templates=templates)

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

    visitor = JinjaVisitor(custom_templates=templates)

    node = FootnoteNode(
        [TextNode("Just some text.")], "5", "someanchor", "someanchor-def"
    )

    result = visitor.visit(node)

    assert result == "Just some text. - 5 - someanchor - someanchor-def"


def test_inline_reference_node():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "reference-somecontent.j2": (
            "{{ content_type }} - {{ name }} - {{category}} - {{ content }} - "
            "{{ number }} - {{ title }} - {{ reference_anchor }} - {{ content_anchor }}"
        ),
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = ReferenceNode(
        "somecontent",
        "somevalue",
        "somecategory",
        [TextNode("Just some text.")],
        "5",
        SentenceNode([TextNode("Some title")]),
        "someanchor",
        "someanchor-def",
    )

    result = visitor.visit(node)

    assert result == (
        "somecontent - somevalue - somecategory - Just some text. "
        "- 5 - Some title - someanchor - someanchor-def"
    )


def test_inline_class_node():
    templates = {
        "text.j2": "{{ value }}",
        "class.j2": "{{ classes | join(',') }} - {{ content }}",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = ClassNode(["class1", "class2"], TextNode("Just some text."))

    result = visitor.visit(node)

    assert result == "class1,class2 - Just some text."


def test_inline_link_node():
    templates = {
        "text.j2": "{{ value }}",
        "link.j2": "{{ target }} - {{ text }}",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = LinkNode(target="sometarget", text="sometext")

    result = visitor.visit(node)

    assert result == "sometarget - sometext"


def test_inline_image_node():
    templates = {
        "text.j2": "{{ value }}",
        "image.j2": "{{ uri }} - {{ alt_text }} - {{ width }}x{{ height }}",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = ImageNode(uri="someuri", alt_text="sometext", width="100", height="400")

    result = visitor.visit(node)

    assert result == "someuri - sometext - 100x400"


def test_inline_list_item_node():
    templates = {
        "text.j2": "{{ value }}",
        "list_item.j2": "{{ level }} - {{ content }}",
    }

    visitor = JinjaVisitor(custom_templates=templates)

    node = ListItemNode("4", TextNode("Just some text."))

    result = visitor.visit(node)

    assert result == "4 - Just some text."
