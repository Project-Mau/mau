from unittest.mock import patch

from mau.parsers.nodes import DocumentNode
from mau.parsers.main_parser import MainParser
from mau.visitors.html_visitor import HTMLVisitor

from tests.helpers import (
    dedent,
    init_parser_factory,
    init_ast_factory,
    ast_test_factory,
    remove_indentation,
    visitlist_factory,
)

init_parser = init_parser_factory(MainParser)

init_ast = init_ast_factory(MainParser)

_test = ast_test_factory(MainParser, HTMLVisitor)

visitlist = visitlist_factory(HTMLVisitor)


def test_text():
    v = HTMLVisitor()

    output = v.visit(
        {
            "type": "text",
            "value": "This is text",
        }
    )

    assert output == "This is text"


def test_sentence():
    v = HTMLVisitor()

    output = v.visit(
        {"type": "sentence", "content": [{"type": "text", "value": "This is text"}]}
    )

    assert output == "This is text"


def test_paragraph():
    source = "This is text"

    expected = ["<p>This is text</p>"]

    _test(source, expected)


def test_horizontal_rule():
    source = "---"

    expected = ["<hr>"]

    _test(source, expected)


def test_style_underscore():
    source = "_This is text_"

    expected = ["<p><em>This is text</em></p>"]

    _test(source, expected)


def test_text_that_contains_styles():
    source = "This _is_ text"

    expected = ["<p>This <em>is</em> text</p>"]

    _test(source, expected)


def test_style_star():
    source = "*This is text*"

    expected = ["<p><strong>This is text</strong></p>"]

    _test(source, expected)


def test_style_verbatim():
    source = "`This is text`"

    expected = ["<p><code>This is text</code></p>"]

    _test(source, expected)


def test_class():
    source = "[classname]#text with that class#"

    expected = ['<p><span class="classname">text with that class</span></p>']

    _test(source, expected)


def test_link():
    source = '[link](https://somedomain.org/the/path,"link text")'

    expected = ['<p><a href="https://somedomain.org/the/path">link text</a></p>']

    _test(source, expected)


def test_inline_image():
    source = "[image](/the/path.jpg)"

    expected = ['<p><span class="image"><img src="/the/path.jpg"></span></p>']

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_header_level_3(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = "=== Title of the section"

    expected = ['<h3 id="XXXXXX">Title of the section</h3>']

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
        remove_indentation(
            """
            <blockquote>
              <p>Learn about the Force, Luke.</p>
              <cite>Star Wars, 1977</cite>
            </blockquote>
            """
        )
    ]

    _test(source, expected)


def test_admonition():
    source = dedent(
        """
        [admonition,aclass,anicon,alabel]
        ----
        This is my test admonition
        ----
        """
    )

    expected = [
        remove_indentation(
            """
            <div class="admonition aclass">
              <i class="anicon"></i>
              <div class="content">
                <div class="title">alabel</div>
                <div>
                  <p>This is my test admonition</p>
                </div>
              </div>
            </div>
            """
        )
    ]

    _test(source, expected)


def test_raw():
    source = dedent(
        """
        [raw]
        ----
        <div class="someclass">
          <p>This is HTML</>
        </div>
        ----
        """
    )

    expected = ["""<div class="someclass">\n  <p>This is HTML</>\n</div>"""]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_block(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = dedent(
        """
        [sometype]
        ++++
        = A block

        This contains headers, paragraphs and blocks

        ++++
        """
    )

    expected = [
        remove_indentation(
            """
            <div class="sometype">
              <div class="content">
                <h1 id="XXXXXX">A block</h1>
                <p>This contains headers, paragraphs and blocks</p>
              </div>
            </div>
            """
        )
    ]

    _test(source, expected)


def test_basic_block_attributes():
    source = dedent(
        """
        [sometype,mayattr1=value1]
        ++++
        This contains headers, paragraphs and blocks
        ++++
        """
    )

    expected = [
        remove_indentation(
            """
            <div class="sometype">
              <div class="content">
                <p>This contains headers, paragraphs and blocks</p>
              </div>
            </div>
            """
        )
    ]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_basic_block_title(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = dedent(
        """
        . Title
        [sometype]
        ++++
        = A block

        This contains headers, paragraphs and blocks

        ++++
        """
    )

    expected = [
        remove_indentation(
            """
            <div class="sometype">
              <div class="title">Title</div>
              <div class="content">
                <h1 id="XXXXXX">A block</h1>
                <p>This contains headers, paragraphs and blocks</p>
              </div>
            </div>
            """
        )
    ]

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

    assert result == [
        remove_indentation(
            """
            <html>
              <head>
              </head>
              <body>
                <p>This is text</p>
              </body>
            </html>
            """
        )
    ]


def test_no_document():
    parser = init_parser(
        dedent(
            """
            This is text
            """
        )
    )
    parser.parse()

    document = DocumentNode(parser.nodes, no_document=True)
    node = document.asdict()

    result = visitlist([node])

    assert result == ["<p>This is text</p>"]


def test_list_unordered():
    source = dedent(
        """
        * Item 1
        ** Item 1.1
        * Item 2
        """
    )

    expected = [
        remove_indentation(
            """
            <ul>
              <li>Item 1
                <ul>
                  <li>Item 1.1</li>
                </ul>
              </li>
              <li>Item 2</li>
            </ul>
            """
        )
    ]

    _test(source, expected)


def test_list_ordered():
    source = dedent(
        """
        # Item 1
        ## Item 1.1
        # Item 2
        """
    )

    expected = [
        remove_indentation(
            """
            <ol>
              <li>Item 1
                <ol>
                  <li>Item 1.1</li>
                </ol>
              </li>
              <li>Item 2</li>
            </ol>
            """
        )
    ]

    _test(source, expected)


def test_list_mixed():
    source = dedent(
        """
        # Item 1
        ** Item 1.1
        # Item 2
        """
    )

    expected = [
        remove_indentation(
            """
            <ol>
              <li>Item 1
                <ul>
                  <li>Item 1.1</li>
                </ul>
              </li>
              <li>Item 2</li>
            </ol>
            """
        )
    ]

    _test(source, expected)


def test_include_image():
    source = "<< image:/path/to/it.jpg"

    expected = [
        remove_indentation(
            """
            <div class="imageblock">
              <div class="content">
                <img src="/path/to/it.jpg">
              </div>
            </div>
            """
        )
    ]

    _test(source, expected)


def test_include_image_alt_text():
    source = dedent(
        """
        [alt_text="This is a beautiful image"]
        << image:/path/to/it.jpg
        """
    )

    expected = [
        remove_indentation(
            """
            <div class="imageblock">
              <div class="content">
                <img src="/path/to/it.jpg" alt="This is a beautiful image">
              </div>
            </div>
            """
        )
    ]

    _test(source, expected)


def test_include_image_title():
    source = dedent(
        """
        . A nice _caption_
        << image:/path/to/it.jpg
        """
    )

    expected = [
        remove_indentation(
            """
            <div class="imageblock">
              <div class="content">
                <img src="/path/to/it.jpg">
                <div class="title">A nice <em>caption</em></div>
              </div>
            </div>
            """
        )
    ]

    _test(source, expected)


def test_macro():
    source = "[unknown](This is an unknown macro)"

    expected = ["<p></p>"]

    _test(source, expected)
