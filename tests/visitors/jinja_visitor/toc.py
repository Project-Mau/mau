from mau.environment.environment import Environment
from mau.nodes.toc import TocEntryNode, TocNode
from mau.visitors.jinja_visitor import JinjaVisitor


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
