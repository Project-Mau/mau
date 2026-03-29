from mau.environment.environment import Environment
from mau.nodes.block import BlockNode
from mau.nodes.inline import TextNode
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.paragraph import ParagraphLineNode, ParagraphNode
from mau.test_helpers import NullMessageHandler
from mau.visitors.jinja_visitor import JinjaVisitor


def test_paragraph_without_parent_and_arguments():
    # Check that the node without parent and
    # arguments uses the plain template named
    # after its type.

    templates = {
        "text.j2": "{{ value }}",
        "paragraph-line.j2": "{{ content }}",
        "paragraph.j2": "{{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    node = ParagraphNode(
        content=[ParagraphLineNode(content=[TextNode("Just some text")])],
    )

    result = visitor.visit(node)

    assert result == "Just some text"


def test_paragraph_with_single_tag():
    # Check that the node with a single tag
    # uses first the template that includes
    # that tag.

    templates = {
        "text.j2": "{{ value }}",
        "paragraph-line.j2": "{{ content }}",
        "paragraph.tg_tag1.j2": "##{{ content }}##",
        "paragraph.j2": "{{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    tags = ["tag1"]

    node = ParagraphNode(
        content=[
            ParagraphLineNode(content=[TextNode("Just some text")]),
        ],
        arguments=NodeArguments(
            tags=tags,
        ),
    )

    result = visitor.visit(node)

    assert result == "##Just some text##"


def test_paragraph_with_multiple_tags():
    # Check that the node with a multiple tags
    # tries to use the templates that include
    # the tags in order.

    templates = {
        "text.j2": "{{ value }}",
        "paragraph-line.j2": "{{ content }}",
        "paragraph.tg_tag2.j2": "##{{ content }}##",
        "paragraph.j2": "{{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    tags = ["tag1", "tag2"]

    node = ParagraphNode(
        content=[
            ParagraphLineNode(content=[TextNode("Just some text")]),
        ],
        arguments=NodeArguments(
            tags=tags,
        ),
    )

    result = visitor.visit(node)

    assert result == "##Just some text##"


def test_paragraph_with_subtype():
    # Check that the node with a subtype tries
    # to use the template that includes it.

    templates = {
        "text.j2": "{{ value }}",
        "paragraph-line.j2": "{{ content }}",
        "paragraph.somesubtype.j2": "##{{ content }}##",
        "paragraph.j2": "{{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    subtype = "somesubtype"

    node = ParagraphNode(
        content=[
            ParagraphLineNode(content=[TextNode("Just some text")]),
        ],
        arguments=NodeArguments(
            subtype=subtype,
        ),
    )

    result = visitor.visit(node)

    assert result == "##Just some text##"


def test_paragraph_with_subtype_and_tags():
    # Check that the node with a subtype and
    # tags tries to use the template that
    # includes both.

    templates = {
        "text.j2": "{{ value }}",
        "paragraph-line.j2": "{{ content }}",
        "paragraph.somesubtype.tg_tag2.j2": "##{{ content }}##",
        "paragraph.somesubtype.j2": "{{ content }}",
        "paragraph.j2": "{{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    tags = ["tag1", "tag2"]
    subtype = "somesubtype"

    node = ParagraphNode(
        content=[
            ParagraphLineNode(content=[TextNode("Just some text")]),
        ],
        arguments=NodeArguments(
            tags=tags,
            subtype=subtype,
        ),
    )

    result = visitor.visit(node)

    assert result == "##Just some text##"


def test_paragraph_with_parent():
    # Check that the node with a parent tries
    # to use the template that includes the
    # parent's type.

    templates = {
        "text.j2": "{{ value }}",
        "paragraph-line.j2": "{{ content }}",
        "paragraph.pt_block.j2": "##{{ content }}##",
        "paragraph.j2": "{{ content }}",
    }

    environment = Environment()
    environment.dupdate(templates, "mau.visitor.templates.custom")
    visitor = JinjaVisitor(NullMessageHandler(), environment)

    block_node = BlockNode()
    node = ParagraphNode(
        content=[ParagraphLineNode(content=[TextNode("Just some text")])],
        parent=block_node,
    )

    result = visitor.visit(node)

    assert result == "##Just some text##"
