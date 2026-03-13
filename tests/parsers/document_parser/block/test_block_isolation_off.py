from unittest.mock import patch

from mau.lexers.document_lexer import DocumentLexer
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    check_parent,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


@patch("mau.parsers.managers.toc_manager.default_header_internal_id")
def test_non_isolated_block_adds_headers_to_global_toc(mock_header_internal_id):
    mock_header_internal_id.return_value = "XXYY"

    source = """
    [isolate=false]
    ----
    = Block header
    ----
    """

    parser = runner(source)

    assert len(parser.toc_manager.headers) == 1


def test_non_isolated_block_adds_footnotes_to_global_list():
    source = """
    [isolate=false]
    ----
    Some text with a [footnote](note).

    [footnote=note]
    ####
    Some text.
    ####
    ----
    """

    parser = runner(source)

    assert len(parser.footnotes_manager.footnotes_dict) == 1
    assert len(parser.footnotes_manager.bodies) == 1
    assert "note" in parser.footnotes_manager.bodies


def test_non_isolated_block_parenthood():
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
