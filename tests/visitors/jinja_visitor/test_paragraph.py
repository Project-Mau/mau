from mau.environment.environment import Environment
from mau.nodes.inline import TextNode
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.paragraph import ParagraphLineNode, ParagraphNode
from mau.test_helpers import NullMessageHandler
from mau.visitors.jinja_visitor import JinjaVisitor


def test_page_paragraph_node():
    templates = {
        "text.j2": "{{ value }}",
        "paragraph-line.j2": "{{ content }}",
        "paragraph.j2": "{{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    unnamed_args = ["arg1", "arg2"]
    named_args = {"key1": "value1"}
    tags = ["tag1", "tag2"]

    node = ParagraphNode(
        content=[ParagraphLineNode(content=[TextNode("Just some text")])],
        arguments=NodeArguments(
            unnamed_args=unnamed_args,
            named_args=named_args,
            tags=tags,
            subtype="subtype1",
        ),
    )

    result = visitor.visit(node)

    assert result == "Just some text"
