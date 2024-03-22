from mau.nodes.paragraph import ParagraphNode
from mau.visitors.jinja_visitor import JinjaVisitor
from mau.environment.environment import Environment
from mau.nodes.inline import TextNode


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
