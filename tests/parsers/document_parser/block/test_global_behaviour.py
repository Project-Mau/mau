import pytest

from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.nodes.block import BlockNode
from mau.nodes.inline import TextNode
from mau.nodes.label import LabelNode
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


def test_parse_block_title_and_arguments():
    source = """
    . Just a title
    [arg1, *subtype1, #tag1, key1=value1]
    ----
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=[],
                labels={
                    "title": LabelNode(
                        "title",
                        content=[
                            TextNode(
                                "Just a title",
                                info=NodeInfo(context=generate_context(1, 2, 1, 14)),
                            )
                        ],
                    ),
                },
                arguments=NodeArguments(
                    unnamed_args=["arg1"],
                    named_args={"key1": "value1"},
                    tags=["tag1"],
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(3, 0, 4, 4),
                ),
            ),
        ],
    )


def test_block_classes_single_class():
    source = """
    [*subtype1,classes=cls1]
    ----
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=["cls1"],
                arguments=NodeArguments(
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(2, 0, 3, 4),
                ),
            )
        ],
    )


def test_block_classes_multiple_classes():
    source = """
    [*subtype1,classes="cls1,cls2"]
    ----
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=["cls1", "cls2"],
                arguments=NodeArguments(
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(2, 0, 3, 4),
                ),
            )
        ],
    )


def test_block_engine():
    source = """
    [*subtype,engine=doesnotexist]
    ----
    ----
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Engine 'doesnotexist' is not available."
    assert exc.value.message.context == generate_context(2, 0, 3, 4)
