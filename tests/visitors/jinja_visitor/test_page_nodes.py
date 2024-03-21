from mau.environment.environment import Environment
from mau.nodes.footnotes import FootnoteNode, FootnotesNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import (
    BlockNode,
    ContentImageNode,
    ContentNode,
    HeaderNode,
    HorizontalRuleNode,
    ParagraphNode,
)
from mau.nodes.references import ReferencesEntryNode, ReferencesNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.nodes.toc import TocEntryNode, TocNode
from mau.visitors.jinja_visitor import JinjaVisitor


def test_page_horizontal_rule_node():
    templates = {
        "text.j2": "{{ value }}",
        "horizontal_rule.j2": (
            "--- - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %} - "
            "{{ tags | join(',') }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")

    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = HorizontalRuleNode(args=args, kwargs=kwargs, tags=tags)

    result = visitor.visit(node)

    assert result == "--- - arg1,arg2 - key1:value1 - tag1,tag2"


def test_page_paragraph_node():
    templates = {
        "text.j2": "{{ value }}",
        "paragraph.j2": (
            "{{ content }} - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %} - "
            "{{ tags | join(',') }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = ParagraphNode(
        TextNode("Just some text"), args=args, kwargs=kwargs, tags=tags
    )

    result = visitor.visit(node)

    assert result == "Just some text - arg1,arg2 - key1:value1 - tag1,tag2"


def test_page_header_node():
    templates = {
        "text.j2": "{{ value }}",
        "header.j2": (
            "{{ value }} - {{ level }} - {{ anchor }} - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %} - "
            "{{ tags | join(',') }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = HeaderNode(
        "Just some text", "3", "someanchor", args=args, kwargs=kwargs, tags=tags
    )

    result = visitor.visit(node)

    assert (
        result
        == "Just some text - 3 - someanchor - arg1,arg2 - key1:value1 - tag1,tag2"
    )


def test_page_content_node():
    templates = {
        "text.j2": "{{ value }}",
        "content.sometype.j2": (
            "{{ title }} - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %} - "
            "{{ tags | join(',') }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = ContentNode(
        "sometype", TextNode("sometitle"), args=args, kwargs=kwargs, tags=tags
    )

    result = visitor.visit(node)

    assert result == "sometitle - arg1,arg2 - key1:value1 - tag1,tag2"


def test_content_image_node():
    templates = {
        "text.j2": "{{ value }}",
        "content_image.j2": (
            "{{ uri }} - {{ alt_text }} - {{ classes | join(',') }} - "
            "{{ title }} - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %} - "
            "{{ tags | join(',') }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = ContentImageNode(
        "someuri",
        "sometext",
        ["class1", "class2"],
        TextNode("sometitle"),
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert (
        result
        == "someuri - sometext - class1,class2 - sometitle - arg1,arg2 - key1:value1 - tag1,tag2"
    )


def test_page_block_node_standard_block_template():
    templates = {
        "text.j2": "{{ value }}",
        "block.j2": (
            "{{ subtype }} - {{ content }} - {{ secondary_content }} - "
            "{{ classes | join(',') }} - {{ title }} - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %} - "
            "{{ tags | join(',') }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = BlockNode(
        subtype="someblock",
        content=[TextNode("my content")],
        secondary_content=[TextNode("my secondary content")],
        classes=["class1", "class2"],
        title=TextNode("sometitle"),
        engine="someengine",
        preprocessor="somepreprocessor",
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert result == (
        "someblock - my content - my secondary content - class1,class2 - "
        "sometitle - arg1,arg2 - key1:value1 - tag1,tag2"
    )


def test_page_block_node_subtype_template_has_precedence():
    templates = {
        "text.j2": "{{ value }}",
        "block.someblock.j2": "The subtype template",
        "block.j2": "The wrong template",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = BlockNode(
        subtype="someblock",
        content=[TextNode("my content")],
        secondary_content=[TextNode("my secondary content")],
        classes=["class1", "class2"],
        title=TextNode("sometitle"),
        engine="someengine",
        preprocessor="somepreprocessor",
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert result == "The subtype template"


def test_page_block_node_engine_template_has_precedence():
    templates = {
        "text.j2": "{{ value }}",
        "block.someengine.j2": "The engine template",
        "block.someblock.j2": "The wrong template",
        "block.j2": "The wrong template",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = BlockNode(
        subtype="someblock",
        content=[TextNode("my content")],
        secondary_content=[TextNode("my secondary content")],
        classes=["class1", "class2"],
        title=TextNode("sometitle"),
        engine="someengine",
        preprocessor="somepreprocessor",
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert result == "The engine template"


def test_page_block_node_engine_and_subtype_template_has_precedence():
    templates = {
        "text.j2": "{{ value }}",
        "block.someengine.someblock.j2": "The engine+block template",
        "block.someengine.j2": "The wrong template",
        "block.someblock.j2": "The wrong template",
        "block.j2": "The wrong template",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = BlockNode(
        subtype="someblock",
        content=[TextNode("my content")],
        secondary_content=[TextNode("my secondary content")],
        classes=["class1", "class2"],
        title=TextNode("sometitle"),
        engine="someengine",
        preprocessor="somepreprocessor",
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert result == "The engine+block template"


def test_page_toc_node():
    templates = {
        "text.j2": "{{ value }}",
        "toc.j2": (
            "{{ entries }} - {{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %} - "
            "{{ tags | join(',') }}"
        ),
        "toc_entry.j2": (
            "{{ anchor }}:{{ value }}{% if children %} - " "{{ children }}{% endif %}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
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
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert result == (
        "header-1:Header 1 - header-1-1:Header 1.1header-2:Header 2 - "
        "arg1,arg2 - key1:value1 - tag1,tag2"
    )


def test_page_footnotes_node():
    templates = {
        "text.j2": "{{ value }}",
        "footnotes.j2": "{{ entries }}",
        "footnotes_entry.j2": (
            "{{ content }}:{{ number }}:" "{{ content_anchor }}:{{ reference_anchor }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = FootnotesNode(
        entries=[
            FootnoteNode(
                [TextNode("Footnote 1")], "1", "anchor-1", "anchor-1-def"
            ).to_entry(),
            FootnoteNode(
                [TextNode("Footnote 2")], "2", "anchor-2", "anchor-2-def"
            ).to_entry(),
        ],
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert (
        result == "Footnote 1:1:anchor-1-def:anchor-1Footnote 2:2:anchor-2-def:anchor-2"
    )


def test_page_references_multiple_nodes():
    templates = {
        "sentence.j2": "{{ content }}",
        "paragraph.j2": "{{ content }}",
        "text.j2": "{{ value }}",
        "references.j2": "{{ entries }}",
        "references_entry.j2": (
            "{{ content_type }}:{{ content }}:{{ number }}:"
            "{{ title }}:{{ content_anchor }}:{{ reference_anchor }}::"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
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
                title=SentenceNode([TextNode("Some title 1.1")]),
                reference_anchor="ref-content_type1-1-XXYY",
                content_anchor="cnt-content_type1-1-XXYY",
            ),
            ReferencesEntryNode(
                "content_type1",
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
                title=SentenceNode([TextNode("Some title 1.2")]),
                reference_anchor="ref-content_type1-2-XXYY",
                content_anchor="cnt-content_type1-2-XXYY",
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
                number=3,
                title=SentenceNode([TextNode("Some title 2.1")]),
                reference_anchor="ref-content_type2-3-XXYY",
                content_anchor="cnt-content_type2-3-XXYY",
            ),
        ],
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert result == (
        "content_type1:Content type 1, value 1:1:Some title 1.1:"
        "cnt-content_type1-1-XXYY:ref-content_type1-1-XXYY::"
        "content_type1:Content type 1, value 2:2:Some title 1.2:"
        "cnt-content_type1-2-XXYY:ref-content_type1-2-XXYY::"
        "content_type2:Content type 2, value 1:3:Some title 2.1:"
        "cnt-content_type2-3-XXYY:ref-content_type2-3-XXYY::"
    )


def test_source_node():
    templates = {
        "text.j2": "{{ value }}",
        "callout.j2": "",
        "callouts_entry.j2": "{{ marker }} - {{ value }}",
        "source.default.somelang.j2": "The subtype+language template",
        "source.somelang.j2": "The language template",
        "source.default.j2": "The subtype template",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

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

    assert result == "The subtype+language template"
