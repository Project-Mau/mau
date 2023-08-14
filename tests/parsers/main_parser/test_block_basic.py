import pytest
from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import BlockNode, ParagraphNode
from mau.parsers.base_parser import ParserError
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
            blocktype="default",
            content=[],
            secondary_content=[],
            classes=[],
            title=None,
            engine="default",
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
            blocktype="default",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("This is a paragraph."),
                        ]
                    )
                ),
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine="default",
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
            blocktype="default",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("The answer is 42."),
                        ]
                    )
                ),
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine="default",
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
            blocktype="default",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("The answer is 42."),
                        ]
                    )
                ),
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine="default",
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]


def test_block_without_closing_fences():
    parser = init_parser("----")

    with pytest.raises(ParserError):
        parser.parse()


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
            blocktype="default",
            content=[],
            secondary_content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode(
                                (
                                    "This is a paragraph that gets eaten. "
                                    "This is a second paragraph that gets eaten."
                                )
                            ),
                        ]
                    )
                ),
            ],
            classes=[],
            title=None,
            engine="default",
            preprocessor="none",
            args=[],
            kwargs={},
        ),
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This paragraph appears in the output."),
                ]
            )
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
            blocktype="default",
            content=[
                BlockNode(
                    blocktype="default",
                    content=[],
                    secondary_content=[],
                    classes=[],
                    title=None,
                    engine="default",
                    preprocessor="none",
                    args=[],
                    kwargs={},
                )
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine="default",
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]
