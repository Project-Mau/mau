from mau.environment.environment import Environment
from mau.nodes.footnotes import FootnoteNode, FootnotesNode
from mau.nodes.inline import TextNode
from mau.visitors.jinja_visitor import JinjaVisitor


def test_page_footnotes_node():
    templates = {
        "text.j2": "{{ value }}",
        "footnotes.j2": "{{ entries }}",
        "footnotes_entry.j2": (
            "{{ content }}:{{ number }}:" "{{ content_anchor }}:{{ reference_anchor }}"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = FootnotesNode(
        children=[
            FootnoteNode(
                children=[TextNode("Footnote 1")],
                number="1",
                reference_anchor="anchor-1",
                content_anchor="anchor-1-def",
            ).to_entry(),
            FootnoteNode(
                children=[TextNode("Footnote 2")],
                number="2",
                reference_anchor="anchor-2",
                content_anchor="anchor-2-def",
            ).to_entry(),
        ],
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert (
        result == "Footnote 1:1:anchor-1-def:anchor-1Footnote 2:2:anchor-2-def:anchor-2"
    )
