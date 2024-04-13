from mau.environment.environment import Environment
from mau.nodes.block import BlockNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.visitors.jinja_visitor import JinjaVisitor


def test_page_paragraph_node():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "paragraph.j2": (
            "{{ content }} - {{ title }} - {{ args | join(',') }} - "
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
        title=SentenceNode(children=[TextNode("sometitle")]),
        children=[TextNode("Just some text")],
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert result == "Just some text - sometitle - arg1,arg2 - key1:value1 - tag1,tag2"


def test_page_paragraph_node_inside_block():
    templates = {
        "block.j2": "{{ content }}",
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

    node = BlockNode(
        subtype="section",
        children=[
            ParagraphNode(
                children=[TextNode("Just some text")],
                args=["arg1", "arg2"],
                kwargs={"key1": "value1"},
                tags=["tag1", "tag2"],
            ),
        ],
    )

    result = visitor.visit(node)

    assert result == "Just some text - arg1,arg2 - key1:value1 - tag1,tag2"
