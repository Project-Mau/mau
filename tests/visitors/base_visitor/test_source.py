from mau.environment.environment import Environment
from mau.nodes.inline import TextNode
from mau.nodes.source import CalloutNode, CalloutsEntryNode, SourceNode
from mau.visitors.base_visitor import BaseVisitor


def test_source_node():
    visitor = BaseVisitor(Environment())

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
        args=["arg1", "arg2"],
        kwargs={"key1": "value1"},
        tags=["tag1", "tag2"],
    )

    result = visitor.visit(node)

    assert result == {
        "data": {
            "type": "source",
            "subtype": None,
            "callouts": [
                {
                    "data": {
                        "marker": "imp",
                        "type": "callouts_entry",
                        "value": "This is an import",
                    }
                },
                {
                    "data": {
                        "marker": "env",
                        "type": "callouts_entry",
                        "value": "Environment variables are paramount",
                    }
                },
            ],
            "classes": [],
            "code": [
                {"data": {"type": "text", "value": "import sys"}},
                {"data": {"type": "text", "value": "import: os"}},
                {"data": {"type": "text", "value": ""}},
                {
                    "data": {
                        "type": "text",
                        "value": 'print(os.environ["HOME"])',
                    }
                },
            ],
            "highlights": [],
            "language": "somelang",
            "lines": 4,
            "markers": [
                None,
                {"data": {"type": "callout", "line": 1, "marker": "imp"}},
                None,
                {"data": {"type": "callout", "line": 3, "marker": "env"}},
            ],
            "preprocessor": None,
            "title": {},
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "tags": ["tag1", "tag2"],
        }
    }
