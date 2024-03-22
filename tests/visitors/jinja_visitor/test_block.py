from mau.environment.environment import Environment
from mau.nodes.block import BlockNode
from mau.nodes.inline import TextNode
from mau.visitors.jinja_visitor import JinjaVisitor


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
