from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.header import HeaderNode
from mau.nodes.inline import StyleNode, TextNode
from mau.nodes.label import LabelNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
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


def test_header_level_1():
    environment = Environment()
    environment["mau.parser.header_internal_id_function"] = lambda node: "XXXXXY"

    source = """
    = Title of the section
    """

    parser = runner(source, environment)

    expected_nodes = [
        HeaderNode(
            1,
            internal_id="XXXXXY",
            content=[
                TextNode(
                    "Title of the section",
                    info=NodeInfo(context=generate_context(1, 2, 1, 22)),
                )
            ],
            info=NodeInfo(context=generate_context(1, 0, 1, 22)),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_header_level_3():
    environment = Environment()
    environment["mau.parser.header_internal_id_function"] = lambda node: "XXXXXY"

    source = """
    === Title of a subsection
    """

    parser = runner(source, environment)

    expected_nodes = [
        HeaderNode(
            3,
            internal_id="XXXXXY",
            content=[
                TextNode(
                    "Title of a subsection",
                    info=NodeInfo(context=generate_context(1, 4, 1, 25)),
                )
            ],
            info=NodeInfo(context=generate_context(1, 0, 1, 25)),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_header_text_styles():
    environment = Environment()
    environment["mau.parser.header_internal_id_function"] = lambda node: "XXXXXY"

    source = """
    === Header with *a style*
    """

    parser = runner(source, environment)

    expected_nodes = [
        HeaderNode(
            3,
            internal_id="XXXXXY",
            content=[
                TextNode(
                    "Header with ",
                    info=NodeInfo(context=generate_context(1, 4, 1, 16)),
                ),
                StyleNode(
                    "star",
                    content=[
                        TextNode(
                            "a style",
                            info=NodeInfo(context=generate_context(1, 17, 1, 24)),
                        ),
                    ],
                    info=NodeInfo(context=generate_context(1, 16, 1, 25)),
                ),
            ],
            info=NodeInfo(context=generate_context(1, 0, 1, 25)),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_header_attributes():
    environment = Environment()
    environment["mau.parser.header_internal_id_function"] = lambda node: "XXXXXY"

    source = """
    [arg1, #tag1, *subtype1, key1=value1]
    = Title of the section
    """

    parser = runner(source, environment)

    expected_nodes = [
        HeaderNode(
            1,
            internal_id="XXXXXY",
            content=[
                TextNode(
                    "Title of the section",
                    info=NodeInfo(context=generate_context(2, 2, 2, 22)),
                )
            ],
            arguments=NodeArguments(
                unnamed_args=["arg1"],
                named_args={"key1": "value1"},
                tags=["tag1"],
                subtype="subtype1",
            ),
            info=NodeInfo(
                context=generate_context(2, 0, 2, 22),
            ),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_header_attributes_can_overwrite_ids():
    source = """
    [arg1, #tag1, *subtype1, internal_id=some_internal_id, name=some_alias]
    = Title of the section
    """

    parser = runner(source)

    expected_nodes = [
        HeaderNode(
            1,
            internal_id="some_internal_id",
            name="some_alias",
            content=[
                TextNode(
                    "Title of the section",
                    info=NodeInfo(context=generate_context(2, 2, 2, 22)),
                )
            ],
            arguments=NodeArguments(
                unnamed_args=["arg1"],
                named_args={},
                tags=["tag1"],
                subtype="subtype1",
            ),
            info=NodeInfo(
                context=generate_context(2, 0, 2, 22),
            ),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_header_usese_labels():
    environment = Environment()
    environment["mau.parser.header_internal_id_function"] = lambda node: "XXXXXY"

    source = """
    . This is a label
    = Title of the section
    """

    parser = runner(source, environment)

    expected_nodes = [
        HeaderNode(
            1,
            internal_id="XXXXXY",
            content=[
                TextNode(
                    "Title of the section",
                    info=NodeInfo(context=generate_context(2, 2, 2, 22)),
                )
            ],
            labels={
                "title": LabelNode(
                    "title",
                    content=[
                        TextNode(
                            "This is a label",
                            info=NodeInfo(context=generate_context(1, 2, 1, 17)),
                        )
                    ],
                ),
            },
            info=NodeInfo(context=generate_context(2, 0, 2, 22)),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_header_uses_control_positive():
    environment = Environment()
    environment["mau.parser.header_internal_id_function"] = lambda node: "XXXXXY"
    environment["answer"] = "42"

    source = """
    @if answer==42
    = Title of the section
    """

    parser = runner(source, environment)

    expected_nodes = [
        HeaderNode(
            1,
            internal_id="XXXXXY",
            content=[
                TextNode(
                    "Title of the section",
                    info=NodeInfo(context=generate_context(2, 2, 2, 22)),
                )
            ],
            info=NodeInfo(context=generate_context(2, 0, 2, 22)),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)

    assert parser.control_buffer.pop() is None


def test_header_uses_control_negative():
    environment = Environment()
    environment["answer"] = "24"

    source = """
    @if answer==42
    [arg1, arg2]
    . Some title
    = Title of the section
    """

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, [])

    assert parser.arguments_buffer.arguments is None
    assert parser.label_buffer.labels == {}
    assert parser.control_buffer.control is None


def test_header_parenthood():
    source = """
    = Title of the section
    """

    parser = runner(source)

    document_node = parser.output.document

    header_node = parser.nodes[0]

    # The header node must be a
    # child of the document.
    check_parent(document_node, [header_node])

    # All nodes inside the header
    # must be children of the header node.
    check_parent(header_node, header_node.content)


def test_header_parenthood_labels():
    source = """
    . A label
    .role Another label
    = Title of the section
    """

    parser = runner(source)

    header_node = parser.nodes[0]
    label_title = header_node.labels["title"]
    label_role = header_node.labels["role"]

    # Each label must be a child of the
    # list it has been assigned to.
    check_parent(header_node, [label_title])
    check_parent(header_node, [label_role])
    check_parent(label_title, label_title.content)
    check_parent(label_role, label_role.content)
