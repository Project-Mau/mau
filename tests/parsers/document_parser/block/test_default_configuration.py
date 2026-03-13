from unittest.mock import patch

from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.header import HeaderNode
from mau.nodes.include import FootnotesNode, TocNode
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    check_parent,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_default_block_configuration_does_not_add_headers_to_global_toc():
    source = """
    ----
    = Block header
    ----
    """

    parser = runner(source)

    assert len(parser.toc_manager.headers) == 0


def test_default_block_configuration_does_not_add_footnotes_to_global_list():
    source = """
    ----
    Some text with a [footnote](note).

    [footnote=note]
    ####
    Some text.
    ####
    ----
    """

    parser = runner(source)

    assert len(parser.footnotes_manager.footnotes_dict) == 0
    assert len(parser.footnotes_manager.bodies) == 0


@patch("mau.parsers.managers.toc_manager.default_header_internal_id")
def test_default_block_toc_contains_block_headers_only(mock_header_internal_id):
    mock_header_internal_id.return_value = "XXYY"

    source = """
    = Global header

    ----
    = Block header

    << toc
    ----
    """

    parser = runner(source)

    block_node = parser.nodes[1]
    block_header_node: HeaderNode = block_node.content[0]
    block_toc_node: TocNode = block_node.content[1]

    assert len(block_toc_node.plain_entries) == 1
    assert block_toc_node.plain_entries[0] is not block_header_node
    assert block_toc_node.plain_entries[0].level == block_header_node.level
    assert block_toc_node.plain_entries[0].internal_id == block_header_node.internal_id
    assert block_toc_node.plain_entries[0].parent is block_toc_node


def test_default_block_does_not_add_footnotes_to_global_list():
    source = """
    ----
    Some text with a [footnote](note).

    [footnote=note]
    ####
    Some text.
    ####
    ----
    """

    parser = runner(source)

    assert len(parser.footnotes_manager.footnotes_dict) == 0
    assert len(parser.footnotes_manager.bodies) == 0


def test_default_block_footnotes_contains_block_footnotes_only():
    source = """
    Global text with a [footnote](globalnote).

    [footnote=globalnote]
    ####
    Some global text.
    ####

    ----
    Some text with a [footnote](note).

    [footnote=note]
    ####
    Some text.
    ####

    << footnotes
    ----
    """

    parser = runner(source)

    block_node = parser.nodes[1]
    block_footnotes_node: FootnotesNode = block_node.content[1]

    assert len(block_footnotes_node.footnotes) == 1


def test_block_parenthood():
    source = """
    ----
    This is a paragraph.
    ----
    """

    parser = runner(source)

    document_node = parser.output.document

    block_node = parser.nodes[0]

    # All parser nodes must be
    # children of the document node.
    check_parent(document_node, parser.nodes)

    # All nodes inside the block must be
    # children of the block.
    check_parent(block_node, block_node.content)


def test_block_parenthood_labels():
    source = """
    . A label
    .role Another label
    ----
    This is a paragraph.
    ----
    """

    parser = runner(source)

    block_node = parser.nodes[0]
    label_title = block_node.labels["title"]
    label_role = block_node.labels["role"]

    # Each label must be a child of the
    # block it has been assigned to.
    check_parent(block_node, [label_title])
    check_parent(label_title, label_title.content)
    check_parent(block_node, [label_role])
    check_parent(label_role, label_role.content)
