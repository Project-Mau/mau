from mau.environment.environment import Environment
from mau.nodes.content import ContentImageNode, ContentNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.visitors.jinja_visitor import JinjaVisitor


def test_page_content_node():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
        "content.sometype.j2": (
            "{{ title }} - "
            "{{ uris | join(',') }} - "
            "{{ args | join(',') }} - "
            "{% for key, value in kwargs|items %}{{ key }}:{{ value }}{% endfor %} - "
            "{{ tags | join(',') }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = ContentNode(
        "sometype",
        uris=["/uri1", "/uri2"],
        title=SentenceNode(children=[TextNode("sometitle")]),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == "sometitle - /uri1,/uri2 - arg1,arg2 - key1:value1 - tag1,tag2"


def test_content_image_node():
    templates = {
        "text.j2": "{{ value }}",
        "sentence.j2": "{{ content }}",
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

    node = ContentImageNode(
        "someuri",
        "alttext",
        ["class1", "class2"],
        title=SentenceNode(children=[TextNode("sometitle")]),
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert (
        result
        == "someuri - alttext - class1,class2 - sometitle - arg1,arg2 - key1:value1 - tag1,tag2"
    )
