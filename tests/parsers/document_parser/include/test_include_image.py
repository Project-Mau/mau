import pytest

from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.nodes.include import IncludeImageNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_include_image_with_only_path():
    source = """
    << image:/path/to/it.jpg
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeImageNode(
                "/path/to/it.jpg",
                arguments=NodeArguments(
                    unnamed_args=[],
                    named_args={},
                    tags=[],
                    subtype=None,
                ),
                info=NodeInfo(
                    context=generate_context(1, 0, 1, 8),
                ),
            ),
        ],
    )


def test_include_image_with_alt_text_and_classes():
    source = """
    << image:/path/to/it.jpg, "Alt text", "class1,class2"
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeImageNode(
                "/path/to/it.jpg",
                "Alt text",
                ["class1", "class2"],
                arguments=NodeArguments(
                    unnamed_args=[],
                    named_args={},
                    tags=[],
                    subtype=None,
                ),
                info=NodeInfo(
                    context=generate_context(1, 0, 1, 8),
                ),
            ),
        ],
    )


def test_include_image_without_uri():
    source = """
    << image"
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Syntax error. You need to specify a URI."
    assert exc.value.message.context == generate_context(1, 0, 1, 8)
