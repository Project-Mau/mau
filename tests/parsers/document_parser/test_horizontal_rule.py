from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.document import HorizontalRuleNode
from mau.nodes.inline import TextNode
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


def test_horizontal_rule():
    source = """
    ---
    """

    parser = runner(source)

    expected_nodes = [
        HorizontalRuleNode(
            info=NodeInfo(context=generate_context(1, 0, 1, 3)),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_horizontal_rule_with_arguments():
    source = """
    [arg1,#tag1,*subtype1,key1=value1]
    ---
    """

    parser = runner(source)

    expected_nodes = [
        HorizontalRuleNode(
            arguments=NodeArguments(
                unnamed_args=["arg1"],
                named_args={
                    "key1": "value1",
                },
                tags=["tag1"],
                subtype="subtype1",
            ),
            info=NodeInfo(
                context=generate_context(2, 0, 2, 3),
            ),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_horizontal_rule_with_labels():
    source = """
    .details This is a label
    ---
    """

    parser = runner(source)

    expected_nodes = [
        HorizontalRuleNode(
            labels={
                "details": LabelNode(
                    "details",
                    content=[
                        TextNode(
                            "This is a label",
                            info=NodeInfo(
                                context=generate_context(1, 9, 1, 24),
                            ),
                        )
                    ],
                ),
            },
            info=NodeInfo(
                context=generate_context(2, 0, 2, 3),
            ),
        )
    ]

    compare_nodes_sequence(parser.nodes, expected_nodes)


def test_horizontal_rule_with_control():
    environment = Environment()
    environment["answer"] = "24"

    source = """
    @if answer==42
    [arg1, arg2]
    . Some title
    ---
    """

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, [])

    assert parser.arguments_buffer.arguments is None
    assert parser.label_buffer.labels == {}
    assert parser.control_buffer.control is None


def test_list_parenthood():
    source = """
    ---
    """

    parser = runner(source)

    document_node = parser.output.document

    # All parser nodes must be
    # children of the document node.
    check_parent(document_node, parser.nodes)


def test_horizontal_rule_parenthood_labels():
    source = """
    . A label
    .role Another label
    ---
    """

    parser = runner(source)

    horizontal_rule_node = parser.nodes[0]
    label_title = horizontal_rule_node.labels["title"]
    label_role = horizontal_rule_node.labels["role"]

    # Each label must be a child of the
    # horizontal rule it has been assigned to.
    check_parent(horizontal_rule_node, [label_title])
    check_parent(horizontal_rule_node, [label_role])
    check_parent(label_title, label_title.content)
    check_parent(label_role, label_role.content)
