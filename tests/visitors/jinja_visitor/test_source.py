from mau.environment.environment import Environment
from mau.nodes.inline import TextNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.visitors.jinja_visitor import JinjaVisitor


def test_source_node():
    templates = {
        "text.j2": "{{ value }}",
        "callout.j2": "",
        "callouts_entry.j2": "{{ marker }} - {{ value }}",
        "source.custom.j2": "The custom template",
        "source.j2": "The default template",
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
        subtype="custom",
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == "The custom template"
