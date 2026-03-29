from unittest.mock import mock_open, patch

import pytest

from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.nodes.include import IncludeRawNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.raw import RawLineNode
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    compare_nodes_sequence,
    dedent,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_include_raw():
    # This tests that Mau can include
    # a file that contains text
    # and add it to the current
    # document as raw lines.

    source = """
    << raw:/path/to/it
    """

    RAW_TEXT = dedent("""
    This is a paragraph.
    This is part of the same paragraph.

    This is another paragraph.
    """)

    with patch("builtins.open", mock_open(read_data=RAW_TEXT)) as mock_file:
        parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeRawNode(
                "/path/to/it",
                arguments=NodeArguments(
                    unnamed_args=[],
                    named_args={},
                    tags=[],
                    subtype=None,
                ),
                info=NodeInfo(
                    context=generate_context(1, 0, 1, 6),
                ),
                content=[
                    RawLineNode(
                        value="This is a paragraph.",
                        info=NodeInfo(context=generate_context(1, 0, 1, 6)),
                    ),
                    RawLineNode(
                        value="This is part of the same paragraph.",
                        info=NodeInfo(context=generate_context(1, 0, 1, 6)),
                    ),
                    RawLineNode(
                        value="",
                        info=NodeInfo(context=generate_context(1, 0, 1, 6)),
                    ),
                    RawLineNode(
                        value="This is another paragraph.",
                        info=NodeInfo(context=generate_context(1, 0, 1, 6)),
                    ),
                ],
            )
        ],
    )

    mock_file.assert_called_with("/path/to/it", "r", encoding="utf-8")

    assert parser.output.include_calls == []


def test_include_mau_without_uri():
    source = """
    << raw"
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Syntax error. You need to specify a URI."
    assert exc.value.message.context == generate_context(1, 0, 1, 6)


def test_include_mau_invalid_uri():
    source = """
    << raw:doesnotexist.mau
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "File 'doesnotexist.mau' cannot be read."
    assert exc.value.message.context == generate_context(1, 0, 1, 6)
