from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.inline import SentenceNode, StyleNode, TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_admonition():
    source = """
    [*admonition,someclass,someicon,somelabel]
    ----
    Content
    ----
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="admonition",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("Content"),
                        ]
                    )
                ),
            ],
            secondary_content=[],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={"class": "someclass", "icon": "someicon", "label": "somelabel"},
        )
    ]


def test_parse_block_quote_attribution_in_secondary_content():
    source = """
    [*quote]
    ----
    Learn about the Force, Luke.
    ----
    _Star Wars_, 1977
    """

    assert runner(source).nodes == [
        BlockNode(
            subtype="quote",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("Learn about the Force, Luke."),
                        ]
                    )
                ),
            ],
            secondary_content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            StyleNode(
                                "underscore",
                                SentenceNode(
                                    [
                                        TextNode("Star Wars"),
                                    ]
                                ),
                            ),
                            TextNode(", 1977"),
                        ]
                    )
                ),
            ],
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]
