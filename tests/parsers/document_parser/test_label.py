from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.inline import StyleNode, TextNode
from mau.nodes.label import LabelNode
from mau.nodes.node import NodeInfo
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_label():
    source = """
    . Some title
    """

    parser = runner(source)
    labels = parser.label_buffer.pop()

    label = labels["title"]
    assert isinstance(label, LabelNode)
    assert label.role == "title"

    compare_nodes_sequence(
        label.content,
        [
            TextNode(
                "Some title",
                info=NodeInfo(context=generate_context(1, 2, 1, 12)),
            )
        ],
    )


def test_label_with_spaces():
    source = """
    .   Some title
    """

    parser = runner(source)
    labels = parser.label_buffer.pop()

    compare_nodes_sequence(
        labels["title"].content,
        [
            TextNode(
                "Some title",
                info=NodeInfo(context=generate_context(1, 4, 1, 14)),
            )
        ],
    )


def test_label_role():
    source = """
    .arole Some label
    """

    parser = runner(source)
    labels = parser.label_buffer.pop()

    label = labels["arole"]
    assert isinstance(label, LabelNode)
    assert label.role == "arole"

    compare_nodes_sequence(
        label.content,
        [
            TextNode(
                "Some label",
                info=NodeInfo(context=generate_context(1, 7, 1, 17)),
            )
        ],
    )


def test_label_multiple():
    source = """
    . Some title
    .arole Some label
    """

    parser = runner(source)
    labels = parser.label_buffer.pop()

    assert set(labels.keys()) == set(["title", "arole"])

    compare_nodes_sequence(
        labels["title"].content,
        [
            TextNode(
                "Some title",
                info=NodeInfo(context=generate_context(1, 2, 1, 12)),
            )
        ],
    )

    compare_nodes_sequence(
        labels["arole"].content,
        [
            TextNode(
                "Some label",
                info=NodeInfo(context=generate_context(2, 7, 2, 17)),
            )
        ],
    )


def test_label_can_contain_mau_syntax():
    source = """
    . Some _title_
    """

    parser = runner(source)
    labels = parser.label_buffer.pop()

    compare_nodes_sequence(
        labels["title"].content,
        [
            TextNode(
                "Some ",
                info=NodeInfo(context=generate_context(1, 2, 1, 7)),
            ),
            StyleNode(
                "underscore",
                content=[
                    TextNode(
                        "title",
                        info=NodeInfo(context=generate_context(1, 8, 1, 13)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 7, 1, 14)),
            ),
        ],
    )
