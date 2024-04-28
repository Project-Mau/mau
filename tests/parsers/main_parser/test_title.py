from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.content import ContentNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.nodes import Node
from mau.parsers.main_parser import MainParser
from mau.text_buffer.context import Context

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_initial_title():
    source = """
    """

    parser = runner(source)

    assert parser.title == (None, None)


def test_push_title():
    source = """
    """

    parser = runner(source)

    parser._push_title("Just a title", Context(42, 128, "main", ".Just a title"))

    assert parser.title == (
        "Just a title",
        Context(42, 128, "main", ".Just a title"),
    )


def test_pop_title():
    source = """
    """

    node = Node()

    parser = runner(source)

    parser._push_title("Just a title", Context(42, 128, "main", ".Just a title"))

    title_node = parser._pop_title(node)

    assert title_node == SentenceNode(
        children=[
            TextNode("Just a title"),
        ]
    )
    assert title_node.parent == node
    assert title_node.parent_position == "title"


def test_parse_title():
    source = """
    .Just a title
    """

    parser = runner(source)

    assert parser.title == (
        "Just a title",
        Context(1, 0, "main", ".Just a title"),
    )


def test_block_uses_title():
    source = """
    .Just a title
    ----
    ----
    """

    parser = runner(source)

    assert parser.nodes == [
        BlockNode(
            subtype=None,
            classes=[],
            title=SentenceNode(
                children=[
                    TextNode("Just a title"),
                ]
            ),
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]

    assert parser.title == (None, None)


def test_include_content_uses_title():
    source = """
    .Just a title
    << type:uri1
    """

    parser = runner(source)

    assert parser.nodes == [
        ContentNode(
            content_type="type",
            uris=["uri1"],
            title=SentenceNode(
                children=[
                    TextNode("Just a title"),
                ]
            ),
        )
    ]

    assert parser.title == (None, None)
