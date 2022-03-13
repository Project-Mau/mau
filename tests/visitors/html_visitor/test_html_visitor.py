import pytest

from unittest.mock import patch

from mau.parsers.nodes import DocumentNode, ContainerNode
from mau.parsers.base_parser import ParserError
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


def test_style_verbatim_with_angle_brackets():
    source = "`This is <a placeholder>`"

    expected = ["<p><code>This is &lt;a placeholder&gt;</code></p>"]

    _test(source, expected)


def test_class_old_style():
    source = "[classname]#text with that class#"

    expected = ['<p><span class="classname">text with that class</span></p>']

    _test(source, expected)


def test_class_new_style():
    source = '[class]("text with classes", "class1,class2")'

    expected = ['<p><span class="class1 class2">text with classes</span></p>']

    _test(source, expected)


def test_link():
    source = '[link](https://somedomain.org/the/path,"link text")'

    expected = ['<p><a href="https://somedomain.org/the/path">link text</a></p>']

    _test(source, expected)


def test_link_with_ampersand():
    source = '[link]("https://s3.console.aws.amazon.com/s3/home?region=eu-west-1&region=eu-west-1")'

    expected = [
        '<p><a href="https://s3.console.aws.amazon.com/s3/home?region=eu-west-1&amp;region=eu-west-1">https://s3.console.aws.amazon.com/s3/home?region=eu-west-1&amp;region=eu-west-1</a></p>'
    ]

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


def test_quote_attribution_in_secondary_content_supports_styles():
    source = dedent(
        """
        [quote]
        ----
        Learn about the Force, Luke.
        ----
        _Star Wars_, 1977
        """
    )

    expected = [
        remove_indentation(
            """
            <blockquote>
              <p>Learn about the Force, Luke.</p>
              <cite><p><em>Star Wars</em>, 1977</p></cite>
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
        """<div class="sometype"><div class="content"><h1 id="XXXXXX">A block</h1>\n<p>This contains headers, paragraphs and blocks</p></div></div>"""
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
        """<div class="sometype"><div class="title">Title</div><div class="content"><h1 id="XXXXXX">A block</h1>\n<p>This contains headers, paragraphs and blocks</p></div></div>"""
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


def test_container():
    parser = init_parser(
        dedent(
            """
            This is text
            """
        )
    )
    parser.parse()

    document = ContainerNode(parser.nodes)
    node = document.asdict()

    result = visitlist([node])

    assert result == [
        remove_indentation(
            """
            <p>This is text</p>
            """
        )
    ]


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
                <img src="/path/to/it.jpg" />
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
                <img src="/path/to/it.jpg" alt="This is a beautiful image" />
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
                <img src="/path/to/it.jpg" />
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


def test_macro_template():
    v = HTMLVisitor()
    v.default_templates["macro.html"] = "whatever"

    ast = init_ast("[unknown](This is an unknown macro)")

    output = [v.visit(node) for node in ast]

    assert output == ["<p>whatever</p>"]


def test_macro_uses_specific_template():
    v = HTMLVisitor()
    v.default_templates["macro.html"] = "whatever"
    v.default_templates["macro-unknown.html"] = "the right one"

    ast = init_ast("[unknown](This is an unknown macro)")

    output = [v.visit(node) for node in ast]

    assert output == ["<p>the right one</p>"]


def test_macro_provides_args_and_kwargs():
    v = HTMLVisitor()
    v.default_templates["macro.html"] = "whatever"
    v.default_templates["macro-unknown.html"] = "{{ args[0] }} - {{ kwargs.name}}"

    ast = init_ast('[unknown]("some text", name=mau)')

    output = [v.visit(node) for node in ast]

    assert output == ["<p>some text - mau</p>"]


def test_macro_alias_value_for_first_unnamed_arg():
    v = HTMLVisitor()
    v.default_templates["macro.html"] = "whatever"
    v.default_templates["macro-unknown.html"] = "{{ value }} - {{ kwargs.name}}"

    ast = init_ast('[unknown]("some text", name=mau)')

    output = [v.visit(node) for node in ast]

    assert output == ["<p>some text - mau</p>"]


def test_block_engine_raw():
    source = dedent(
        """
        [block, engine=raw]
        ----
        <div class="someclass">
          <p>This is HTML</>
        </div>
        ----
        """
    )

    expected = [
        """<div class="block"><div class="content"><div class="someclass">\n  <p>This is HTML</>\n</div></div></div>"""
    ]

    _test(source, expected)


def test_block_engine_default():
    source = dedent(
        """
        = Header out

        [block, engine=default]
        ----
        = Header in

        ::toc:
        ----
        """
    )

    parser = init_parser(source)
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=parser.toc)

    assert result == [
        '<h1 id="header-out">Header out</h1>',
        '<div class="block"><div class="content"><h1 id="header-in">Header in</h1>\n<div><ul><li><a href="#header-out">Header out</a></li><li><a href="#header-in">Header in</a></li></ul></div></div></div>',
    ]


def test_block_engine_mau():
    source = dedent(
        """
        = Header out

        [block, engine=mau]
        ----
        = Header in

        ::toc:
        ----
        """
    )

    parser = init_parser(source)
    parser.parse()

    result = visitlist([node.asdict() for node in parser.nodes], toc=parser.toc)

    assert result == [
        '<h1 id="header-out">Header out</h1>',
        '<div class="block"><div class="content"><h1 id="header-in">Header in</h1><div><ul><li><a href="#header-in">Header in</a></li></ul></div></div></div>',
    ]


def test_block_template():
    v = HTMLVisitor()
    v.default_templates["block.html"] = "whatever"

    ast = init_ast(
        dedent(
            """
            [block]
            ----
            Primary content
            ----
            Secondary content
            """
        )
    )

    output = [v.visit(node) for node in ast]

    assert output == ["whatever"]


def test_block_uses_specific_template():
    v = HTMLVisitor()
    v.default_templates["block.html"] = "whatever"
    v.default_templates["block-unknown.html"] = "the right one"

    ast = init_ast(
        dedent(
            """
            [unknown]
            ----
            Primary content
            ----
            Secondary content
            """
        )
    )

    output = [v.visit(node) for node in ast]

    assert output == ["the right one"]


def test_block_supports_kwargs():
    v = HTMLVisitor()
    v.default_templates["block.html"] = "whatever"
    v.default_templates[
        "block-unknown.html"
    ] = "{{ kwargs.name }} - {{ kwargs.colour }}"

    ast = init_ast(
        dedent(
            """
            [unknown, name=myblock, colour=green]
            ----
            ----
            """
        )
    )

    output = [v.visit(node) for node in ast]

    assert output == ["myblock - green"]


def test_block_does_not_support_args():
    v = HTMLVisitor()
    v.default_templates["block.html"] = "whatever"
    v.default_templates["block-unknown.html"] = ""

    with pytest.raises(ParserError):
        ast = init_ast(
            dedent(
                """
                [unknown, value1, value2]
                ----
                Primary content
                ----
                Secondary content
                """
            )
        )


@patch("mau.parsers.main_parser.header_anchor")
def test_command_consumes_args(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = dedent(
        """
        ::unknown:unused1,unuse2=value2

        [sometype]
        ++++
        = A block

        This contains headers, paragraphs and blocks

        ++++
        """
    )

    expected = [
        "",
        """<div class="sometype"><div class="content"><h1 id="XXXXXX">A block</h1>\n<p>This contains headers, paragraphs and blocks</p></div></div>""",
    ]

    _test(source, expected)
