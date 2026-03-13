from mau.environment.environment import Environment
from mau.nodes.footnote import FootnoteNode
from mau.nodes.header import HeaderNode
from mau.nodes.inline import StyleNode, TextNode, VerbatimNode
from mau.nodes.macro import (
    MacroClassNode,
    MacroFootnoteNode,
    MacroHeaderNode,
    MacroImageNode,
    MacroLinkNode,
    MacroNode,
)
from mau.nodes.node_arguments import NodeArguments
from mau.test_helpers import NullMessageHandler
from mau.visitors.jinja_visitor import JinjaVisitor


def test_inline_text_node():
    templates = {
        "text.j2": "#{{ value }}#",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = TextNode("Just some text.")

    result = visitor.visit(node)

    assert result == "#Just some text.#"


def test_inline_verbatim_node():
    templates = {
        "verbatim.j2": "`{{ value }}`",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = VerbatimNode("Just some text.")

    result = visitor.visit(node)

    assert result == "`Just some text.`"


def test_inline_style_node_star():
    templates = {
        "text.j2": "{{ value }}",
        "style.style__star.j2": "*{{ content }}*",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = StyleNode("star", content=[TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == "*Just some text.*"


def test_inline_style_node_underscore():
    templates = {
        "text.j2": "{{ value }}",
        "style.style__underscore.j2": "_{{ content }}_",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = StyleNode("underscore", content=[TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == "_Just some text._"


def test_inline_style_node_tilde():
    templates = {
        "text.j2": "{{ value }}",
        "style.style__tilde.j2": "~{{ content }}~",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = StyleNode("tilde", content=[TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == "~Just some text.~"


def test_inline_style_node_caret():
    templates = {
        "text.j2": "{{ value }}",
        "style.style__caret.j2": "^{{ content }}^",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = StyleNode("caret", content=[TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == "^Just some text.^"


def test_inline_macro_node():
    templates = {
        "text.j2": "{{ value }}",
        "macro.name__somename.j2": (
            "{{ name }} - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %}"
        ),
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = MacroNode(
        "somename",
        arguments=NodeArguments(
            unnamed_args=["arg1", "arg2"],
            named_args={"key1": "value1"},
        ),
    )

    result = visitor.visit(node)

    assert result == "somename - arg1,arg2 - key1:value1"


def test_inline_macro_footnote_node():
    templates = {
        "text.j2": "{{ value }}",
        "macro-footnote.j2": (
            "{{ footnote.content }} - {{ footnote.name }} - "
            "{{ footnote.public_id }} - {{ footnote.internal_id }}"
        ),
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = MacroFootnoteNode(
        name="somenote",
        footnote=FootnoteNode(
            content=[TextNode("Just some text.")],
            name="somenote",
            public_id="public_id",
            internal_id="internal_id",
        ),
    )

    result = visitor.visit(node)

    assert result == "Just some text. - somenote - public_id - internal_id"


def test_inline_class_node():
    templates = {
        "text.j2": "{{ value }}",
        "macro-class.j2": "{{ classes | join(',') }} - {{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = MacroClassNode(["class1", "class2"], content=[TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == "class1,class2 - Just some text."


def test_inline_link_node():
    templates = {
        "text.j2": "{{ value }}",
        "macro-link.j2": "{{ target }} - {{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = MacroLinkNode(target="sometarget", content=[TextNode("sometext")])

    result = visitor.visit(node)

    assert result == "sometarget - sometext"


def test_inline_header_node():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "macro-header.j2": "#{{ header.internal_id }} - {{ content }}",
        "header.j2": "#{{ internal_id }}  {{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    header_node = HeaderNode(
        level=2,
        content=[TextNode("Header")],
        internal_id="XXXXXX",
        name="someid",
    )

    node = MacroHeaderNode(
        target_name="someid",
        header=header_node,
        content=[
            TextNode("sometext"),
        ],
    )

    result = visitor.visit(node)

    assert result == "#XXXXXX - sometext"


def test_inline_image_node():
    templates = {
        "text.j2": "{{ value }}",
        "macro-image.j2": "{{ uri }} - {{ alt_text }} - {{ width }}x{{ height }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = MacroImageNode(uri="someuri", alt_text="sometext", width="100", height="400")

    result = visitor.visit(node)

    assert result == "someuri - sometext - 100x400"
