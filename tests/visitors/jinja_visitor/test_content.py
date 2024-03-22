from mau.environment.environment import Environment
from mau.nodes.content import ContentImageNode, ContentNode
from mau.nodes.inline import TextNode
from mau.visitors.jinja_visitor import JinjaVisitor


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
