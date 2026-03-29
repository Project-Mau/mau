from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.header import HeaderNode
from mau.nodes.include import TocItemNode, TocNode
from mau.nodes.inline import TextNode
from mau.nodes.label import LabelNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.parsers.document_parser import DocumentParser
from mau.parsers.managers.toc_manager import extract_text
from mau.test_helpers import (
    check_parent,
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_include_toc_empty():
    source = """
    << toc
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            TocNode(
                nested_entries=[],
                plain_entries=[],
                info=NodeInfo(context=generate_context(1, 0, 1, 6)),
            )
        ],
    )


def test_include_toc_supports_inline_arguments():
    source = """
    << toc:arg1,#tag1,*subtype1,key1=value1
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            TocNode(
                nested_entries=[],
                plain_entries=[],
                arguments=NodeArguments(
                    unnamed_args=["arg1"],
                    named_args={"key1": "value1"},
                    tags=["tag1"],
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(1, 0, 1, 6),
                ),
            )
        ],
    )


def test_include_toc_supports_boxed_arguments():
    source = """
    [arg1, #tag1, *subtype1, key1=value1]
    << toc
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            TocNode(
                nested_entries=[],
                plain_entries=[],
                arguments=NodeArguments(
                    unnamed_args=["arg1"],
                    named_args={"key1": "value1"},
                    tags=["tag1"],
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(2, 0, 2, 6),
                ),
            )
        ],
    )


def test_include_toc_supports_labels():
    source = """
    . Some label
    << toc
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            TocNode(
                nested_entries=[],
                plain_entries=[],
                labels={
                    "title": LabelNode(
                        "title",
                        content=[
                            TextNode(
                                "Some label",
                                info=NodeInfo(context=generate_context(1, 2, 1, 12)),
                            )
                        ],
                    ),
                },
                info=NodeInfo(context=generate_context(2, 0, 2, 6)),
            )
        ],
    )


def test_include_toc_supports_control():
    environment = Environment()
    environment["answer"] = "24"

    source = """
    @if answer==42
    [arg1, arg2]
    . Some title
    << toc
    """

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, [])

    assert parser.arguments_buffer.arguments is None
    assert parser.label_buffer.labels == {}
    assert parser.control_buffer.control is None


def test_include_toc_with_entries():
    def _header_internal_id(node: HeaderNode) -> str:
        text = extract_text(node.content)

        return f"{text}-XXXXXX"

    environment = Environment()
    environment["mau.parser.header_internal_id_function"] = _header_internal_id

    source = """
    = Header 1
    == Header 1.1
    = Header 2

    << toc
    """

    parser = runner(source, environment)

    header_1_1 = HeaderNode(
        level=2,
        internal_id="Header 1.1-XXXXXX",
        content=[
            TextNode(
                "Header 1.1",
                info=NodeInfo(context=generate_context(2, 3, 2, 13)),
            )
        ],
        info=NodeInfo(context=generate_context(2, 0, 2, 13)),
        parent=parser.parent_node,
    )

    header_1 = HeaderNode(
        level=1,
        internal_id="Header 1-XXXXXX",
        content=[
            TextNode(
                "Header 1",
                info=NodeInfo(context=generate_context(1, 2, 1, 10)),
            )
        ],
        info=NodeInfo(context=generate_context(1, 0, 1, 10)),
        parent=parser.parent_node,
    )

    header_2 = HeaderNode(
        level=1,
        internal_id="Header 2-XXXXXX",
        content=[
            TextNode(
                "Header 2",
                info=NodeInfo(context=generate_context(3, 2, 3, 10)),
            )
        ],
        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
        parent=parser.parent_node,
    )

    toc_item_1_1 = TocItemNode(header=header_1_1)

    toc_item_1 = TocItemNode(header=header_1, entries=[toc_item_1_1])

    toc_item_2 = TocItemNode(header=header_2)

    node_toc = TocNode(
        nested_entries=[
            toc_item_1,
            toc_item_2,
        ],
        plain_entries=[
            header_1,
            header_1_1,
            header_2,
        ],
        info=NodeInfo(context=generate_context(5, 0, 5, 6)),
    )

    compare_nodes_sequence(
        parser.nodes,
        [
            header_1,
            header_1_1,
            header_2,
            node_toc,
        ],
    )


def test_toc_parenthood():
    source = """
    = Header 1
    == Header 1.1
    = Header 2

    << toc
    """

    parser = runner(source)

    document_node = parser.output.document

    toc_node = parser.nodes[3]

    toc_item_1_node = toc_node.nested_entries[0]
    toc_item_2_node = toc_node.nested_entries[1]
    toc_item_1_1_node = toc_item_1_node.entries[0]

    # All parser nodes must be
    # children of the document node.
    check_parent(document_node, parser.nodes)

    # All plain entries inside the toc are
    # deep copies of headers, so they are
    # children of the toc node.
    check_parent(toc_node, toc_node.plain_entries)

    # All nested entries inside the toc must be
    # children of the included node.
    check_parent(toc_node, [toc_item_1_node, toc_item_2_node, toc_item_1_1_node])


def test_toc_parenthood_labels():
    source = """
    . A label
    .role Another label
    << toc
    """

    parser = runner(source)

    toc_node = parser.nodes[0]
    label_title = toc_node.labels["title"]
    label_role = toc_node.labels["role"]

    # Each label must be a child of the
    # block group it has been assigned to.
    check_parent(toc_node, [label_title])
    check_parent(toc_node, [label_role])
    check_parent(label_title, label_title.content)
    check_parent(label_role, label_role.content)
