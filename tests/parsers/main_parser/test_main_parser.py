import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import StyleNode, TextNode
from mau.nodes.page import ContainerNode, DocumentNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.toc import TocNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_parse_discards_empty_lines():
    source = "\n\n\n\n"

    assert runner(source).nodes == []


def test_parse_output():
    source = ""

    assert runner(source).output == {
        "content": ContainerNode(children=[]),
        "toc": ContainerNode(children=[TocNode()]),
    }


def test_parse_output_custom_content_container():
    source = ""

    environment = Environment()
    document = DocumentNode()
    environment.setvar("mau.parser.content_wrapper", document)

    assert runner(source, environment).output == {
        "content": document,
        "toc": ContainerNode(children=[TocNode()]),
    }


def test_parse_output_custom_toc_container():
    source = ""

    environment = Environment()
    document = DocumentNode(children=[TocNode()])
    environment.setvar("mau.parser.toc_wrapper", document)

    assert runner(source, environment).output == {
        "content": ContainerNode(children=[]),
        "toc": document,
    }


def test_parse_single_line_comments():
    source = "// Just a comment"

    assert runner(source).nodes == []


def test_parse_multi_line_comments():
    source = """
    ////
    This is a
    multiline
    comment
    ////
    """

    assert runner(source).nodes == []


def test_parse_multi_line_comments_with_dangerous_characters():
    source = """
    ////
    .This is a
    [multiline]
    ----
    comment
    ////
    """

    assert runner(source).nodes == []


def test_parse_open_multi_line_comments():
    source = """
    ////
    .This is a
    [multiline]
    ----
    comment
    """

    with pytest.raises(MauErrorException):
        runner(source)


def test_command():
    source = "::somecommand:arg1, arg2, name1=value1, name2=value2"

    assert runner(source).nodes == []


def test_command_without_arguments():
    source = "::somecommand:"

    assert runner(source).nodes == []


def test_style_underscore():
    source = """
    This is _underscore_ text
    """

    assert runner(source).nodes == [
        ParagraphNode(
            children=[
                TextNode("This is "),
                StyleNode(
                    value="underscore",
                    children=[
                        TextNode("underscore"),
                    ],
                ),
                TextNode(" text"),
            ],
        )
    ]


def test_style_at_beginning():
    source = """
    *This is star text*
    """

    assert runner(source).nodes == [
        ParagraphNode(
            children=[
                StyleNode(
                    value="star",
                    children=[
                        TextNode("This is star text"),
                    ],
                ),
            ],
        )
    ]


def test_style_not_closed():
    source = r"""
    This ` is a backtick and this _an underscore
    """

    assert runner(source).nodes == [
        ParagraphNode(
            children=[
                TextNode("This ` is a backtick and this _an underscore"),
            ],
        )
    ]


def test_style_escape_markers():
    source = r"""
    This is \_underscore\_ and this is \`verbatim\`
    """

    assert runner(source).nodes == [
        ParagraphNode(
            children=[
                TextNode("This is _underscore_ and this is `verbatim`"),
            ],
        )
    ]
