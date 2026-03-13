from unittest.mock import patch

import pytest

from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.nodes.block import BlockNode
from mau.nodes.footnote import FootnoteNode
from mau.nodes.include import FootnotesItemNode, FootnotesNode
from mau.nodes.inline import TextNode
from mau.nodes.label import LabelNode
from mau.nodes.list import ListItemNode, ListNode
from mau.nodes.macro import MacroFootnoteNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.paragraph import ParagraphLineNode, ParagraphNode
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    check_parent,
    compare_nodes_map,
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


@patch("mau.parsers.managers.footnotes_manager.default_footnote_unique_id")
def test_include_footnotes_in_paragraphs_are_detected(mock_footnote_unique_id):
    mock_footnote_unique_id.return_value = "XXYY"

    source = """
    This contains a footnote[footnote](somename).

    [footnote=somename]
    ----
    Some text.
    ----
    """

    parser = runner(source)

    footnote_name = "somename"

    footnote_body_nodes = [
        ParagraphNode(
            content=[
                ParagraphLineNode(
                    content=[
                        TextNode(
                            "Some text.",
                            info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                        )
                    ],
                    info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                )
            ],
            info=NodeInfo(context=generate_context(5, 0, 5, 10)),
        )
    ]

    footnote_block_data = BlockNode(content=footnote_body_nodes)

    footnote_data = FootnoteNode(
        name=footnote_name,
        public_id="1",
        internal_id="XXYY",
        content=footnote_body_nodes,
    )

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This contains a footnote",
                                info=NodeInfo(context=generate_context(1, 0, 1, 24)),
                            ),
                            MacroFootnoteNode(
                                name=footnote_name,
                                footnote=footnote_data,
                                info=NodeInfo(context=generate_context(1, 24, 1, 44)),
                            ),
                            TextNode(
                                ".",
                                info=NodeInfo(context=generate_context(1, 44, 1, 45)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 45)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 45)),
            )
        ],
    )

    compare_nodes_sequence(
        [parser.footnotes_manager.bodies[footnote_name]],
        [footnote_block_data],
    )

    compare_nodes_map(
        parser.footnotes_manager.footnotes_dict,
        {footnote_name: footnote_data},
    )


@patch("mau.parsers.managers.footnotes_manager.default_footnote_unique_id")
def test_include_footnotes_mention_the_same_footnote_twice(mock_footnote_unique_id):
    mock_footnote_unique_id.return_value = "XXYY"

    source = """
    This contains a footnote[footnote](somename).

    This contains the same footnote[footnote](somename).

    [footnote=somename]
    ----
    Some text.
    ----
    """

    parser = runner(source)

    footnote_name = "somename"

    footnote_body_nodes = [
        ParagraphNode(
            content=[
                ParagraphLineNode(
                    content=[
                        TextNode(
                            "Some text.",
                            info=NodeInfo(context=generate_context(7, 0, 7, 10)),
                        )
                    ],
                    info=NodeInfo(context=generate_context(7, 0, 7, 10)),
                )
            ],
            info=NodeInfo(context=generate_context(7, 0, 7, 10)),
        )
    ]

    footnote_block_data = BlockNode(content=footnote_body_nodes)

    footnote_data = FootnoteNode(
        name=footnote_name,
        public_id="1",
        internal_id="XXYY",
        content=footnote_body_nodes,
    )

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This contains a footnote",
                                info=NodeInfo(context=generate_context(1, 0, 1, 24)),
                            ),
                            MacroFootnoteNode(
                                name=footnote_name,
                                footnote=footnote_data,
                                info=NodeInfo(context=generate_context(1, 24, 1, 44)),
                            ),
                            TextNode(
                                ".",
                                info=NodeInfo(context=generate_context(1, 44, 1, 45)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 45)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 45)),
            ),
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This contains the same footnote",
                                info=NodeInfo(context=generate_context(3, 0, 3, 31)),
                            ),
                            MacroFootnoteNode(
                                name=footnote_name,
                                footnote=footnote_data,
                                info=NodeInfo(context=generate_context(3, 31, 3, 51)),
                            ),
                            TextNode(
                                ".",
                                info=NodeInfo(context=generate_context(3, 51, 3, 52)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(3, 0, 3, 52)),
                    )
                ],
                info=NodeInfo(context=generate_context(3, 0, 3, 52)),
            ),
        ],
    )

    compare_nodes_sequence(
        [parser.footnotes_manager.bodies[footnote_name]],
        [footnote_block_data],
    )

    compare_nodes_map(
        parser.footnotes_manager.footnotes_dict,
        {footnote_name: footnote_data},
    )


@patch("mau.parsers.managers.footnotes_manager.default_footnote_unique_id")
def test_include_footnotes_in_lists_are_processed(mock_footnote_unique_id):
    mock_footnote_unique_id.return_value = "XXYY"

    source = """
    * This contains a footnote[footnote](somename).

    [footnote=somename]
    ----
    Some text.
    ----
    """

    parser = runner(source)

    footnote_name = "somename"

    footnote_body_nodes = [
        ParagraphNode(
            content=[
                ParagraphLineNode(
                    content=[
                        TextNode(
                            "Some text.",
                            info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                        )
                    ],
                    info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                )
            ],
            info=NodeInfo(context=generate_context(5, 0, 5, 10)),
        )
    ]

    footnote_block_data = BlockNode(content=footnote_body_nodes)

    footnote_data = FootnoteNode(
        name=footnote_name,
        public_id="1",
        internal_id="XXYY",
        content=footnote_body_nodes,
    )

    compare_nodes_sequence(
        parser.nodes,
        [
            ListNode(
                ordered=False,
                main_node=True,
                content=[
                    ListItemNode(
                        1,
                        content=[
                            TextNode(
                                "This contains a footnote",
                                info=NodeInfo(context=generate_context(1, 2, 1, 26)),
                            ),
                            MacroFootnoteNode(
                                name=footnote_name,
                                footnote=footnote_data,
                                info=NodeInfo(context=generate_context(1, 26, 1, 46)),
                            ),
                            TextNode(
                                ".",
                                info=NodeInfo(context=generate_context(1, 46, 1, 47)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 47)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 47)),
            )
        ],
    )

    compare_nodes_sequence(
        [parser.footnotes_manager.bodies[footnote_name]],
        [footnote_block_data],
    )

    compare_nodes_map(
        parser.footnotes_manager.footnotes_dict,
        {footnote_name: footnote_data},
    )


@patch("mau.parsers.managers.footnotes_manager.default_footnote_unique_id")
def test_include_footnotes(mock_footnote_unique_id):
    mock_footnote_unique_id.return_value = "XXYY"

    source = """
    This contains a footnote[footnote](somename).

    [footnote=somename]
    ----
    Some text.
    ----

    << footnotes
    """

    parser = runner(source)

    footnote_name = "somename"

    footnote_body_nodes = [
        ParagraphNode(
            content=[
                ParagraphLineNode(
                    content=[
                        TextNode(
                            "Some text.",
                            info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                        )
                    ],
                    info=NodeInfo(context=generate_context(5, 0, 5, 10)),
                )
            ],
            info=NodeInfo(context=generate_context(5, 0, 5, 10)),
        )
    ]

    footnote_node = FootnoteNode(
        name=footnote_name,
        public_id="1",
        internal_id="XXYY",
        content=footnote_body_nodes,
    )

    compare_nodes_sequence(
        parser.nodes,
        [
            ParagraphNode(
                content=[
                    ParagraphLineNode(
                        content=[
                            TextNode(
                                "This contains a footnote",
                                info=NodeInfo(context=generate_context(1, 0, 1, 24)),
                            ),
                            MacroFootnoteNode(
                                name=footnote_name,
                                footnote=footnote_node,
                                info=NodeInfo(context=generate_context(1, 24, 1, 44)),
                            ),
                            TextNode(
                                ".",
                                info=NodeInfo(context=generate_context(1, 44, 1, 45)),
                            ),
                        ],
                        info=NodeInfo(context=generate_context(1, 0, 1, 45)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 1, 45)),
            ),
            FootnotesNode(
                footnotes=[FootnotesItemNode(footnote=footnote_node)],
                info=NodeInfo(context=generate_context(8, 0, 8, 12)),
            ),
        ],
    )


def test_include_footnotes_supports_boxed_arguments():
    source = """
    [arg1, *subtype1, #tag1, key1=value1]
    << footnotes
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            FootnotesNode(
                arguments=NodeArguments(
                    named_args={"key1": "value1"},
                    unnamed_args=["arg1"],
                    subtype="subtype1",
                    tags=["tag1"],
                ),
                info=NodeInfo(
                    context=generate_context(2, 0, 2, 12),
                ),
            ),
        ],
    )


def test_include_footnotes_supports_inline_arguments():
    source = """
    << footnotes:arg1, *subtype1, #tag1, key1=value1
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            FootnotesNode(
                arguments=NodeArguments(
                    named_args={"key1": "value1"},
                    unnamed_args=["arg1"],
                    subtype="subtype1",
                    tags=["tag1"],
                ),
                info=NodeInfo(
                    context=generate_context(1, 0, 1, 12),
                ),
            ),
        ],
    )


def test_include_footnotes_supports_labels():
    source = """
    . Some label
    << footnotes
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            FootnotesNode(
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
                info=NodeInfo(context=generate_context(2, 0, 2, 12)),
            ),
        ],
    )


def test_include_footnotes_supports_control():
    environment = Environment()
    environment["answer"] = "24"

    source = """
    @if answer==42
    [arg1, arg2]
    . Some title
    << footnotes
    """

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, [])

    assert parser.arguments_buffer.arguments is None
    assert parser.label_buffer.labels == {}
    assert parser.control_buffer.control is None


def test_include_footnotes_parenthood():
    source = """
    This contains a footnote[footnote](somename).

    [footnote=somename]
    ----
    Some text.
    ----

    << footnotes
    """

    parser = runner(source)

    document_node = parser.output.document

    footnotes_node = parser.nodes[1]
    footnotes_item_node = footnotes_node.footnotes[0]

    # All parser nodes must be
    # children of the document node.
    check_parent(document_node, parser.nodes)

    # All nodes inside the footnotes list must be
    # children of the included node.
    check_parent(footnotes_node, footnotes_node.footnotes)

    # The footnote inside the footnotes item are
    # floating and are not children of any node.
    check_parent(None, [footnotes_item_node.footnote])


def test_include_footnotes_parenthood_labels():
    source = """
    . A label
    .role Another label
    << footnotes
    """

    parser = runner(source)

    footnotes_node = parser.nodes[0]
    label_title = footnotes_node.labels["title"]
    label_role = footnotes_node.labels["role"]

    # Each label must be a child of the
    # block group it has been assigned to.
    check_parent(footnotes_node, [label_title])
    check_parent(footnotes_node, [label_role])
    check_parent(label_title, label_title.content)
    check_parent(label_role, label_role.content)


def test_include_footnotes_undefined_footnote():
    source = """
    This is a non existing [footnote](nope).
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Footnote 'nope' has not been defined."
    assert exc.value.message.context == generate_context(1, 23, 1, 39)
