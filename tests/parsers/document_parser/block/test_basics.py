from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.nodes.block import BlockNode
from mau.nodes.inline import TextNode
from mau.nodes.node import NodeInfo
from mau.nodes.paragraph import ParagraphLineNode, ParagraphNode
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_block_with_empty_body():
    source = """
    ----
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=[],
                info=NodeInfo(context=generate_context(1, 0, 2, 4)),
            )
        ],
    )


def test_block_content():
    source = """
    ----
    This is a paragraph.
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=[],
                content=[
                    ParagraphNode(
                        content=[
                            ParagraphLineNode(
                                content=[
                                    TextNode(
                                        "This is a paragraph.",
                                        info=NodeInfo(
                                            context=generate_context(2, 0, 2, 20)
                                        ),
                                    )
                                ],
                                info=NodeInfo(context=generate_context(2, 0, 2, 20)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(2, 0, 2, 20)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 3, 4)),
            )
        ],
    )


def test_block_content_variables():
    source = """
    ----
    :answer:42
    The answer is {answer}.
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=[],
                content=[
                    ParagraphNode(
                        content=[
                            ParagraphLineNode(
                                content=[
                                    TextNode(
                                        "The answer is 42.",
                                        info=NodeInfo(
                                            context=generate_context(3, 0, 3, 17)
                                        ),
                                    )
                                ],
                                info=NodeInfo(context=generate_context(3, 0, 3, 23)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(3, 0, 3, 23)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 4, 4)),
            )
        ],
    )


def test_block_content_external_variables():
    source = """
    :answer:42
    ----
    The answer is {answer}.
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=[],
                content=[
                    ParagraphNode(
                        content=[
                            ParagraphLineNode(
                                content=[
                                    TextNode(
                                        "The answer is 42.",
                                        info=NodeInfo(
                                            context=generate_context(3, 0, 3, 17)
                                        ),
                                    )
                                ],
                                info=NodeInfo(context=generate_context(3, 0, 3, 23)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(3, 0, 3, 23)),
                    )
                ],
                info=NodeInfo(context=generate_context(2, 0, 4, 4)),
            )
        ],
    )


def test_block_inside_block():
    source = """
    ----
    ++++
    ++++
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=[],
                content=[
                    BlockNode(
                        classes=[],
                        info=NodeInfo(context=generate_context(2, 0, 3, 4)),
                    )
                ],
                info=NodeInfo(context=generate_context(1, 0, 4, 4)),
            )
        ],
    )


def test_block_uses_control_positive():
    environment = Environment()
    environment["answer"] = "42"

    source = """
    @if answer==42
    ----
    Some text.
    ----
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=[],
                content=[
                    ParagraphNode(
                        content=[
                            ParagraphLineNode(
                                content=[
                                    TextNode(
                                        "Some text.",
                                        info=NodeInfo(
                                            context=generate_context(3, 0, 3, 10)
                                        ),
                                    ),
                                ],
                                info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                            )
                        ],
                        info=NodeInfo(context=generate_context(3, 0, 3, 10)),
                    ),
                ],
                info=NodeInfo(context=generate_context(2, 0, 4, 4)),
            )
        ],
    )

    assert parser.control_buffer.pop() is None


def test_block_uses_control_positive_when_block_is_empty():
    environment = Environment()
    environment["answer"] = "42"

    source = """
    @if answer==42
    ----
    ----
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            BlockNode(
                classes=[],
                info=NodeInfo(context=generate_context(2, 0, 3, 4)),
            )
        ],
    )

    assert parser.control_buffer.pop() is None


def test_block_uses_control_negative():
    environment = Environment()
    environment["answer"] = "24"

    source = """
    @if answer==42
    ----
    This is a block
    ----
    """

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, [])

    assert parser.control_buffer.pop() is None


def test_block_uses_control_negative_when_block_is_empty():
    environment = Environment()
    environment["answer"] = "24"

    source = """
    @if answer==42
    ----
    ----
    """

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, [])

    assert parser.control_buffer.pop() is None


def test_block_control():
    source = """
    :answer:44

    @if answer==42
    [arg1, arg2]
    . Some title
    ----
    This is a block
    ----
    """

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, [])

    assert parser.arguments_buffer.arguments is None
    assert parser.label_buffer.labels == {}
    assert parser.control_buffer.control is None
