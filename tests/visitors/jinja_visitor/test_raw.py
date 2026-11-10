from mau.environment.environment import Environment
from mau.nodes.include import IncludeRawNode
from mau.nodes.raw import RawLineNode, RawNode
from mau.test_helpers import NullMessageHandler
from mau.visitors.jinja_visitor import JinjaVisitor


def _visitor():
    templates = {
        "raw-line.j2": "{{ value }}",
        "raw.j2": "{{ content }}",
        "include-raw.j2": "{{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")

    return JinjaVisitor(NullMessageHandler(), environment)


def test_raw_node_lines_are_joined_with_newlines():
    node = RawNode(
        content=[
            RawLineNode("<pre>"),
            RawLineNode("line 1"),
            RawLineNode("line 2"),
            RawLineNode("</pre>"),
        ]
    )

    result = _visitor().visit(node)

    assert result == "<pre>\nline 1\nline 2\n</pre>"


def test_include_raw_node_lines_are_joined_with_newlines():
    node = IncludeRawNode(
        "file.html",
        content=[
            RawLineNode("<pre>"),
            RawLineNode("line 1"),
            RawLineNode("line 2"),
            RawLineNode("</pre>"),
        ],
    )

    result = _visitor().visit(node)

    assert result == "<pre>\nline 1\nline 2\n</pre>"
