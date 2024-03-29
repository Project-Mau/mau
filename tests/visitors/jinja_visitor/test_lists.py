from mau.environment.environment import Environment
from mau.nodes.inline import TextNode
from mau.nodes.lists import ListItemNode, ListNode
from mau.visitors.jinja_visitor import JinjaVisitor


def test_inline_list_item_node():
    templates = {
        "text.j2": "{{ value }}",
        "list_item.j2": "{{ level }} - {{ content }}",
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    node = ListItemNode(level="4", children=[TextNode("Just some text.")])

    result = visitor.visit(node)

    assert result == "4 - Just some text."


def test_page_list_node():
    templates = {
        "text.j2": "{{ value }}",
        "list_item.j2": "{{ level }}:{{ content }}",
        "list.j2": (
            "{{ ordered }} - {{ items }} - {{ main_node }} - {{ args | join(',') }} - "
            "{{ kwargs|items|map('join', '=')|join(',') }} - {{ tags | join(',') }} - "
            "{{ kwargs.start }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1", "start": 4}
    tags = ["tag1", "tag2"]
    node = ListNode(
        ordered=True,
        main_node=True,
        children=[ListItemNode(level="4", children=[TextNode("Just some text.")])],
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert (
        result
        == "True - 4:Just some text. - True - arg1,arg2 - key1=value1,start=4 - tag1,tag2 - 4"
    )
