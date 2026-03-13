from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.node import NodeInfo
from mau.nodes.raw import RawLineNode, RawNode
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


def test_raw_engine():
    source = """
    [engine=raw]
    ----
    Raw content
    on multiple lines
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            RawNode(
                classes=[],
                content=[
                    RawLineNode(
                        "Raw content",
                        info=NodeInfo(context=generate_context(3, 0, 3, 11)),
                    ),
                    RawLineNode(
                        "on multiple lines",
                        info=NodeInfo(context=generate_context(4, 0, 4, 17)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 5, 4)),
            ),
        ],
    )


def test_raw_engine_no_content():
    source = """
    [engine=raw]
    ----
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            RawNode(
                classes=[],
                content=[],
                info=NodeInfo(context=generate_context(2, 0, 3, 4)),
            ),
        ],
    )


def test_raw_parenthood():
    source = """
    [engine=raw]
    ----
    This is a paragraph.
    ----
    """

    parser = runner(source)

    document_node = parser.output.document

    raw_node = parser.nodes[0]

    # All parser nodes must be
    # children of the document node.
    check_parent(document_node, parser.nodes)

    # All nodes inside the block must be
    # children of the block.
    check_parent(raw_node, raw_node.content)


def test_raw_parenthood_labels():
    source = """
    . A label
    .role Another label
    [engine=raw]
    ----
    This is a paragraph.
    ----
    """

    parser = runner(source)

    raw_node = parser.nodes[0]
    label_title = raw_node.labels["title"]
    label_role = raw_node.labels["role"]

    # Each label must be a child of the
    # raw it has been assigned to.
    check_parent(raw_node, [label_title])
    check_parent(label_title, label_title.content)
    check_parent(raw_node, [label_role])
    check_parent(label_role, label_role.content)
