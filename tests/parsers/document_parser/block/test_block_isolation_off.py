from unittest.mock import patch

import pytest

from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
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


# Test that a link outside a non-isolated block
# can point to a header inside the block.
def test_non_isolated_block_header_link_to_header_inside():
    source = """
    See [header](intro).

    [isolate=false]
    ----
    [name=intro]
    = Introduction
    ----
    """

    parser = runner(source)

    macro = parser.header_links_manager.macros[0]

    assert macro.header is parser.header_links_manager.headers["intro"]


# Test that a link inside a non-isolated block
# can point to a header inside the block and
# that both are visible in the main parser.
def test_non_isolated_block_header_link_and_header_inside():
    source = """
    [isolate=false]
    ----
    [name=intro]
    = Introduction

    See [header](intro).
    ----
    """

    parser = runner(source)

    block_node = parser.nodes[0]
    header_node, paragraph_node = block_node.content
    _, macro_node, _ = paragraph_node.content[0].content

    assert macro_node.type == "macro-header"
    assert macro_node.header is header_node


# Test that headers inside a non-isolated block share
# the names of the main document, so a name
# cannot be used both inside and outside.
def test_non_isolated_block_duplicate_header_name():
    source = """
    [name=intro]
    = Introduction

    [isolate=false]
    ----
    [name=intro]
    = Another introduction
    ----
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Duplicate header id detected: intro"


# Test that a non-isolated block can mention a
# footnote whose body is outside the block.
def test_non_isolated_block_footnote_mention_inside_body_outside():
    source = """
    [isolate=false]
    ----
    Some text with a [footnote](note).
    ----

    [footnote=note]
    ----
    Some text.
    ----
    """

    parser = runner(source)

    macro = parser.footnotes_manager.footnote_macros[0]

    assert macro.footnote is parser.footnotes_manager.footnotes_dict["note"]


# Test that a link inside a non-isolated block
# can point to a header outside the block.
def test_non_isolated_block_header_link_to_header_outside():
    source = """
    [name=intro]
    = Introduction

    [isolate=false]
    ----
    See [header](intro).
    ----
    """

    parser = runner(source)

    macro = parser.header_links_manager.macros[0]

    assert macro.header is parser.header_links_manager.headers["intro"]


# Test that references resolution is deferred through
# multiple levels of non-isolated blocks.
def test_nested_non_isolated_blocks_header_link_to_header_outside():
    source = """
    [name=intro]
    = Introduction

    [isolate=false]
    ----
    [isolate=false]
    ####
    See [header](intro).
    ####
    ----
    """

    parser = runner(source)

    macro = parser.header_links_manager.macros[0]

    assert macro.header is parser.header_links_manager.headers["intro"]
