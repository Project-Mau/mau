from mau.environment.environment import Environment
from mau.nodes.inline import TextNode, SentenceNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.references import ReferencesEntryNode, ReferencesNode
from mau.visitors.jinja_visitor import JinjaVisitor


def test_page_references_multiple_nodes():
    templates = {
        "paragraph.j2": "{{ content }}",
        "sentence.j2": "{{ content }}",
        "text.j2": "{{ value }}",
        "references.j2": "{{ entries }}",
        "references_entry.j2": (
            "{{ content_type }}:{{ content }}:{{ number }}:"
            "{{ title }}:{{ content_anchor }}:{{ reference_anchor }}::"
        ),
    }

    environment = Environment()
    environment.update(templates, "mau.visitor.custom_templates")
    visitor = JinjaVisitor(environment)

    args = ["arg1", "arg2"]
    kwargs = {"key1": "value1"}
    tags = ["tag1", "tag2"]
    node = ReferencesNode(
        content_type=None,
        entries=[
            ReferencesEntryNode(
                "content_type1",
                content=[
                    ParagraphNode(
                        [
                            TextNode("Content type 1, value 1"),
                        ]
                    ),
                ],
                number=1,
                title=SentenceNode([TextNode("Some title 1.1")]),
                reference_anchor="ref-content_type1-1-XXYY",
                content_anchor="cnt-content_type1-1-XXYY",
            ),
            ReferencesEntryNode(
                "content_type1",
                content=[
                    ParagraphNode(
                        [
                            TextNode("Content type 1, value 2"),
                        ]
                    )
                ],
                number=2,
                title=SentenceNode([TextNode("Some title 1.2")]),
                reference_anchor="ref-content_type1-2-XXYY",
                content_anchor="cnt-content_type1-2-XXYY",
            ),
            ReferencesEntryNode(
                "content_type2",
                content=[
                    ParagraphNode(
                        [
                            TextNode("Content type 2, value 1"),
                        ]
                    ),
                ],
                number=3,
                title=SentenceNode([TextNode("Some title 2.1")]),
                reference_anchor="ref-content_type2-3-XXYY",
                content_anchor="cnt-content_type2-3-XXYY",
            ),
        ],
        args=args,
        kwargs=kwargs,
        tags=tags,
    )

    result = visitor.visit(node)

    assert result == (
        "content_type1:Content type 1, value 1:1:Some title 1.1:"
        "cnt-content_type1-1-XXYY:ref-content_type1-1-XXYY::"
        "content_type1:Content type 1, value 2:2:Some title 1.2:"
        "cnt-content_type1-2-XXYY:ref-content_type1-2-XXYY::"
        "content_type2:Content type 2, value 1:3:Some title 2.1:"
        "cnt-content_type2-3-XXYY:ref-content_type2-3-XXYY::"
    )
