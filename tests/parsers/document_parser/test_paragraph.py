from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.inline import StyleNode, TextNode
from mau.nodes.label import LabelNode
from mau.nodes.macro import MacroLinkNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.paragraph import ParagraphLineNode, ParagraphNode
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    check_parent,
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_paragraph():
    source = """
    This is a paragraph.
    This is part of the same paragraph.

    This is another paragraph.
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is a paragraph.",
                                info=NodeInfo(context=generate_context(1, 0, 1, 20)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 20)),
                    ),
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is part of the same paragraph.",
                                info=NodeInfo(context=generate_context(2, 0, 2, 35)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(2, 0, 2, 35)),
                    ),
                ],
                info=NodeInfo(context=generate_context(1, 0, 2, 35)),
            ),
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is another paragraph.",
                                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                    )
                ],
                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
            ),
        ],
    )


def test_paragraph_with_style():
    source = """
    This is a *paragraph*.
    This is part of the same paragraph.

    This is another paragraph.
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is a ",
                                info=NodeInfo(context=generate_context(1, 0, 1, 10)),
                            ),
                            StyleNode(
                                "star",
                                content=[
                                    TextNode(
                                        "paragraph",
                                        info=NodeInfo(
                                            context=generate_context(1, 11, 1, 20)
                                        ),
                                    )
                                ],
                                info=NodeInfo(context=generate_context(1, 10, 1, 21)),
                            ),
                            TextNode(
                                ".",
                                info=NodeInfo(context=generate_context(1, 21, 1, 22)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 22)),
                    ),
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is part of the same paragraph.",
                                info=NodeInfo(context=generate_context(2, 0, 2, 35)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(2, 0, 2, 35)),
                    ),
                ],
                info=NodeInfo(context=generate_context(1, 0, 2, 35)),
            ),
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is another paragraph.",
                                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                    )
                ],
                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
            ),
        ],
    )


def test_paragraph_with_style_on_multiple_lines():
    source = """
    This is a *paragraph
    with style*. This is part of the same paragraph.

    This is another paragraph.
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is a *paragraph",
                                info=NodeInfo(context=generate_context(1, 0, 1, 20)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 20)),
                    ),
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "with style*. This is part of the same paragraph.",
                                info=NodeInfo(context=generate_context(2, 0, 2, 48)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(2, 0, 2, 48)),
                    ),
                ],
                info=NodeInfo(context=generate_context(1, 0, 2, 48)),
            ),
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is another paragraph.",
                                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                    )
                ],
                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
            ),
        ],
    )


def test_paragraph_starting_with_a_macro():
    source = """
    [link](http://some.where,This) is the link I want
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            MacroLinkNode(
                                "http://some.where",
                                content=[
                                    TextNode(
                                        "This",
                                        info=NodeInfo(
                                            context=generate_context(1, 25, 1, 29)
                                        ),
                                    ),
                                ],
                                info=NodeInfo(context=generate_context(1, 0, 1, 30)),
                            ),
                            TextNode(
                                " is the link I want",
                                info=NodeInfo(context=generate_context(1, 30, 1, 49)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 49)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 49)),
            ),
        ],
    )


def test_attributes_paragraph():
    source = """
    [arg1, #tag1, *subtype1, key1=value1]
    This is text
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is text",
                                info=NodeInfo(context=generate_context(2, 0, 2, 12)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(2, 0, 2, 12)),
                    )
                ],
                arguments=NodeArguments(
                    unnamed_args=["arg1"],
                    named_args={"key1": "value1"},
                    tags=["tag1"],
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(2, 0, 2, 12),
                ),
            ),
        ],
    )


def test_paragraph_label():
    source = """
    . A title
    This is text
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is text",
                                info=NodeInfo(context=generate_context(2, 0, 2, 12)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(2, 0, 2, 12)),
                    )
                ],
                labels={
                    "title": LabelNode(
                        "title",
                        content=[
                            TextNode(
                                "A title",
                                info=NodeInfo(context=generate_context(1, 2, 1, 9)),
                            )
                        ],
                    ),
                },
                info=NodeInfo(
                    context=generate_context(2, 0, 2, 12),
                ),
            ),
        ],
    )


def test_paragraph_with_variable():
    source = """
    :variable:cat
    This is a paragraph with a {variable}.
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is a paragraph with a cat.",
                                info=NodeInfo(context=generate_context(2, 0, 2, 31)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(2, 0, 2, 38)),
                    )
                ],
                info=NodeInfo(context=generate_context(2, 0, 2, 38)),
            )
        ],
    )


def test_paragraph_with_namespaced_variable():
    environment = Environment.from_dict({"content": {"animal": "cat"}})
    source = """
    This is a paragraph with a {content.animal}.
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is a paragraph with a cat.",
                                info=NodeInfo(context=generate_context(1, 0, 1, 31)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 44)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 44)),
            )
        ],
    )


def test_paragraph_with_escaped_mau_syntax():
    source = r"""
    \:answer:42
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                ":answer:42",
                                info=NodeInfo(context=generate_context(1, 0, 1, 11)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 11)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 11)),
            )
        ],
    )


def test_paragraph_with_escaped_variable():
    environment = Environment.from_dict({"variable": "cat"})
    source = r"""
    This is a paragraph with a \{variable\}.
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is a paragraph with a {variable}.",
                                info=NodeInfo(context=generate_context(1, 0, 1, 38)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 40)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 40)),
            )
        ],
    )


def test_paragraph_with_variable_containing_syntax():
    environment = Environment.from_dict({"important": "*IMPORTANT*"})
    source = """
    This is {important}
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is ",
                                info=NodeInfo(context=generate_context(1, 0, 1, 8)),
                            ),
                            StyleNode(
                                "star",
                                content=[
                                    TextNode(
                                        "IMPORTANT",
                                        info=NodeInfo(
                                            context=generate_context(1, 9, 1, 18)
                                        ),
                                    ),
                                ],
                                info=NodeInfo(context=generate_context(1, 8, 1, 19)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 19)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 19)),
            )
        ],
    )


def test_paragraph_with_nested_variables():
    source = """
    :answer:42
    :sentence:The answer is {answer}

    {sentence}
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "The answer is 42",
                                info=NodeInfo(context=generate_context(4, 0, 4, 16)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(4, 0, 4, 10)),
                    )
                ],
                info=NodeInfo(context=generate_context(4, 0, 4, 10)),
            )
        ],
    )


def test_paragraph_uses_control_positive():
    environment = Environment.from_dict({"answer": "42"})

    source = """
    @if answer==42
    This is a paragraph.

    This is another paragraph.
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is a paragraph.",
                                info=NodeInfo(context=generate_context(2, 0, 2, 20)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(2, 0, 2, 20)),
                    )
                ],
                info=NodeInfo(context=generate_context(2, 0, 2, 20)),
            ),
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is another paragraph.",
                                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                    )
                ],
                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
            ),
        ],
    )

    assert parser.control_buffer.pop() is None


def test_paragraph_uses_control_negative():
    environment = Environment.from_dict({"answer": "24"})

    source = """
    @if answer==42
    This is a paragraph.

    This is another paragraph.
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This is another paragraph.",
                                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(4, 0, 4, 26)),
                    )
                ],
                info=NodeInfo(context=generate_context(4, 0, 4, 26)),
            ),
        ],
    )

    assert parser.control_buffer.pop() is None


def test_paragraph_control():
    source = """
    :answer:44

    @if answer==42
    [arg1, arg2]
    . Some title
    This paragraph won't be rendered
    """

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, [])

    assert parser.arguments_buffer.arguments is None
    assert parser.label_buffer.labels == {}
    assert parser.control_buffer.control is None


def test_paragraph_parenthood():
    source = """
    This is a paragraph.
    This is part of the same paragraph.

    This is another paragraph.
    """

    parser = runner(source)

    document_node = parser.output.document

    paragraph_node1 = parser.nodes[0]
    paragraph_node2 = parser.nodes[1]

    line_node1 = paragraph_node1.content[0]
    line_node2 = paragraph_node1.content[1]
    line_node3 = paragraph_node2.content[0]

    # Check the number of lines
    # for each paragraph.
    assert len(paragraph_node1.content) == 2
    assert len(paragraph_node2.content) == 1

    # All parser nodes must be
    # children of the document node.
    check_parent(document_node, parser.nodes)

    # Each paragraph line must be a child
    # of the paragraph it belongs to.
    check_parent(paragraph_node1, paragraph_node1.content)
    check_parent(paragraph_node2, paragraph_node2.content)

    # Each node inside the paragraph lines
    # must be a children of the paragraph
    # they belong to.
    check_parent(paragraph_node1, line_node1.content)
    check_parent(paragraph_node1, line_node2.content)
    check_parent(paragraph_node2, line_node3.content)


def test_paragraph_parenthood_labels():
    source = """
    . A label
    .role Another label
    This is a paragraph.
    """

    parser = runner(source)

    paragraph_node = parser.nodes[0]
    label_title = paragraph_node.labels["title"]
    label_role = paragraph_node.labels["role"]

    # Each label must be a child of the
    # paragraph it has been assigned to.
    check_parent(paragraph_node, [label_title])
    check_parent(paragraph_node, [label_role])
    check_parent(label_title, label_title.content)
    check_parent(label_role, label_role.content)
