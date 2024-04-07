from mau.environment.environment import Environment
from mau.nodes.header import HeaderNode
from mau.nodes.inline import TextNode
from mau.visitors.jinja_visitor import JinjaVisitor


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
        value=[TextNode("Just some text")],
        level="3",
        anchor="someanchor",
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert (
        result
        == "Just some text - 3 - someanchor - arg1,arg2 - key1:value1 - tag1,tag2"
    )
