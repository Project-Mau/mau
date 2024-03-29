import pytest
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.inline import TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_parse_block_with_empty_body():
    source = """
    ----
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype=None,
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]


def test_parse_block_content():
    source = """
    ----
    This is a paragraph.
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype=None,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is a paragraph."),
                    ]
                ),
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]


def test_parse_block_content_variables():
    source = """
    ----
    :answer:42
    The answer is {answer}.
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype=None,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("The answer is 42."),
                    ]
                ),
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]


def test_parse_block_content_external_variables():
    source = """
    :answer:42
    ----
    The answer is {answer}.
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype=None,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("The answer is 42."),
                    ]
                ),
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]


def test_block_without_closing_fences():
    with pytest.raises(MauErrorException):
        runner("----")


def test_parse_block_secondary_content():
    source = """
    ----
    ----
    This is a paragraph that gets eaten.
    This is a second paragraph that gets eaten.

    This paragraph appears in the output.
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype=None,
            children=[],
            secondary_children=[
                ParagraphNode(
                    children=[
                        TextNode(
                            (
                                "This is a paragraph that gets eaten. "
                                "This is a second paragraph that gets eaten."
                            )
                        ),
                    ]
                ),
            ],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        ),
        ParagraphNode(
            children=[
                TextNode("This paragraph appears in the output."),
            ]
        ),
    ]


def test_parse_block_inside_block():
    source = """
    ----
    ++++
    ++++
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype=None,
            children=[
                BlockNode(
                    subtype=None,
                    children=[],
                    secondary_children=[],
                    classes=[],
                    title=None,
                    engine=None,
                    preprocessor="none",
                    args=[],
                    kwargs={},
                )
            ],
            secondary_children=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]
