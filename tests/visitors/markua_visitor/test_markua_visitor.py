import pytest

from unittest.mock import patch

from mau.parsers.nodes import DocumentNode
from mau.parsers.main_parser import MainParser
from mau.visitors.markua_visitor import MarkuaVisitor

from tests.helpers import (
    init_parser_factory,
    ast_test_factory,
    init_ast_factory,
    dedent,
    listasdict,
    visitlist_factory,
)

init_parser = init_parser_factory(MainParser)
init_ast = init_ast_factory(MainParser)

_test = ast_test_factory(MainParser, MarkuaVisitor)

visitlist = visitlist_factory(MarkuaVisitor)


def test_text():
    v = MarkuaVisitor()

    output = v.visit(
        {
            "type": "text",
            "value": "This is text",
        }
    )

    assert output == "This is text"


def test_sentence():
    v = MarkuaVisitor()

    output = v.visit(
        {"type": "sentence", "content": [{"type": "text", "value": "This is text"}]}
    )

    assert output == "This is text"


def test_paragraph():
    source = "This is text"

    expected = ["This is text\n"]

    _test(source, expected)


def test_horizontal_rule():
    source = "---"

    expected = ["* * *"]

    _test(source, expected)


def test_style_underscore():
    source = "_This is text_"

    expected = ["*This is text*\n"]

    _test(source, expected)


def test_text_that_contains_styles():
    source = "This _is_ text"

    expected = ["This *is* text\n"]

    _test(source, expected)


def test_style_star():
    source = "*This is text*"

    expected = ["**This is text**\n"]

    _test(source, expected)


def test_style_verbatim():
    source = "`This is text`"

    expected = ["`This is text`\n"]

    _test(source, expected)


def test_class():
    source = "[classname]#text with that class#"

    expected = ["text with that class\n"]

    _test(source, expected)


def test_link():
    source = '[link](https://somedomain.org/the/path,"link text")'

    expected = ["[link text](https://somedomain.org/the/path)\n"]

    _test(source, expected)


def test_link_target_equal_text():
    source = "https://somedomain.org/the/path"

    expected = ["<https://somedomain.org/the/path>\n"]

    _test(source, expected)


def test_inline_image():
    source = '[image](/the/path.jpg,"alt text")'

    expected = ["![alt text](/the/path.jpg)\n"]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_header_level_3(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = "=== Title of the section"

    expected = ["### Title of the section\n"]

    _test(source, expected)


def test_quote():
    source = dedent(
        """
        [quote,"Star Wars, 1977"]
        ----
        Learn about the Force, Luke.
        ----
        """
    )

    expected = [
        dedent(
            """
            {blockquote}
            Learn about the Force, Luke.

            Star Wars, 1977
            {/blockquote}
            """
        )
    ]

    _test(source, expected)


def test_admonition():
    source = dedent(
        """
        [admonition,warning,anicon,alabel]
        ----
        This is my test admonition
        ----
        """
    )

    expected = [
        dedent(
            """
            {blurb, class: warning}
            This is my test admonition
            {/blurb}
            """
        )
    ]

    _test(source, expected)


def test_admonition_not_known():
    ast = init_ast(
        dedent(
            """
            [admonition,something,anicon,alabel]
            ----
            This is my test admonition
            ----
            """
        )
    )

    with pytest.raises(ValueError):
        visitlist(ast)


@patch("mau.parsers.main_parser.header_anchor")
def test_block(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = dedent(
        """
        ++++
        = A block

        This contains headers, paragraphs and blocks

        ++++
        """
    )

    expected = ["# A block\n\nThis contains headers, paragraphs and blocks\n"]

    _test(source, expected)


def test_footnote():
    p = init_parser(
        dedent(
            """
            This is a sentence[footnote](with a note)
            """
        )
    )

    p.parse()
    ast = listasdict(p.nodes)

    result = visitlist(ast, footnotes=[i.asdict() for i in p.footnotes])

    assert result == ["This is a sentence (with a note)\n"]


def test_unordered_list():
    source = dedent(
        """
        * Item 1
        * Item 2
        ** Item 2.1
        *** Item 2.1.1
        * Item 3
        """
    )

    expected = ["\n* Item 1\n* Item 2\n** Item 2.1\n*** Item 2.1.1\n* Item 3\n"]

    _test(source, expected)


def test_ordered_list():
    source = dedent(
        """
        # Item 1
        # Item 2
        ## Item 2.1
        ### Item 2.1.1
        # Item 3
        """
    )

    expected = ["\n* Item 1\n* Item 2\n** Item 2.1\n*** Item 2.1.1\n* Item 3\n"]

    _test(source, expected)


def test_document():
    parser = init_parser(
        dedent(
            """
            This is text
            """
        )
    )
    parser.parse()

    document = DocumentNode(parser.nodes)
    node = document.asdict()

    result = visitlist([node])

    assert result == ["This is text\n"]


def test_source():
    source = dedent(
        """
        [source,language]
        ----
        Some {} source a:=5 code
        ----
        """
    )

    expected = ["``` language\nSome {} source a:=5 code\n```"]

    _test(source, expected)


def test_source_title():
    source = dedent(
        """
        .title
        [source,language]
        ----
        Some {} source a:=5 code
        ----
        """
    )

    expected = ['{caption: "title"}\n``` language\nSome {} source a:=5 code\n```']

    _test(source, expected)


def test_source_callouts():
    source = dedent(
        """
        [source, language]
        ----
        Some {} source a:=5 code:1:
        ----
        1: Callout
        """
    )

    expected = ["``` language\nSome {} source a:=5 code\n```"]

    _test(source, expected)


def test_content_image():
    source = dedent(
        """
        << image:/path/to/it.jpg
        """
    )

    expected = ["![](/path/to/it.jpg)\n"]

    _test(source, expected)


def test_content_image_with_title_and_alt_text():
    source = dedent(
        """
        . Title
        [alt_text="Some text"]
        << image:/path/to/it.jpg
        """
    )

    expected = ['{alt: "Some text"}\n![Title](/path/to/it.jpg)\n']

    _test(source, expected)


def test_command():
    source = dedent(
        """
        ::somecommand:
        """
    )

    expected = [""]

    _test(source, expected)
