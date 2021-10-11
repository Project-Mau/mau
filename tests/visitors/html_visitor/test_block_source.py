import textwrap
from unittest.mock import patch

import pytest

from mau.parsers.main_parser import MainParser
from mau.visitors.visitor import CommandError
from mau.visitors.html_visitor import HTMLVisitor

from tests.helpers import (
    init_parser_factory,
    init_ast_factory,
    ast_test_factory,
)

init_parser = init_parser_factory(MainParser)

init_ast = init_ast_factory(MainParser)

_test = ast_test_factory(MainParser, HTMLVisitor)


@patch("mau.visitors.html_visitor.highlight")
def test_source(mock_highlight):
    mock_highlight.return_value = "XYXYXY"

    source = textwrap.dedent(
        """
        [myblock, engine=source]
        ----
        import os

        print(os.environ["HOME"])
        ----
        """
    )

    expected = ['<div class="myblock"><div class="content">XYXYXY</div></div>']

    _test(source, expected)


@patch("mau.visitors.html_visitor.highlight")
def test_source_indentation(mock_highlight):
    mock_highlight.side_effect = lambda src, lexer, formatter: src

    source = textwrap.dedent(
        """
        [myblock, engine=source]
        ----
        Not indented

            Indented
        ----
        """
    )

    expected = [
        '<div class="myblock"><div class="content">Not indented\n\n    Indented</div></div>'
    ]

    _test(source, expected)


def test_source_callouts():
    source = textwrap.dedent(
        """
        [myblock, engine=source]
        ----
        Some code:1:
        
        Some other code:3:
        ----
        1: This is the first line
        3: This is the second line
        """
    )

    expected = [
        (
            '<div class="myblock">'
            '<div class="content">'
            '<div class="highlight">'
            '<pre><span></span>Some code <span class="callout">1</span>\n\nSome other code <span class="callout">3</span>\n</pre>'
            "</div>\n</div>"
            '<div class="callouts">'
            "<table><tbody>"
            '<tr><td><span class="callout">1</span></td><td>This is the first line</td></tr>'
            '<tr><td><span class="callout">3</span></td><td>This is the second line</td></tr>'
            "</tbody></table>"
            "</div></div>"
        )
    ]

    _test(source, expected)


def test_source_empty_callouts():
    source = textwrap.dedent(
        """
        [myblock, engine=source]
        ----
        Some code:1:
        
        Some other code:3:
        ----
        """
    )

    expected = [
        (
            '<div class="myblock">'
            '<div class="content">'
            '<div class="highlight">'
            '<pre><span></span>Some code <span class="callout">1</span>\n\nSome other code <span class="callout">3</span>\n</pre>'
            "</div>\n</div>"
            "</div>"
        )
    ]

    _test(source, expected)


def test_source_pygments_config():
    source = textwrap.dedent(
        """
        [myblock, engine=source, pygments.hl_lines="1,2,3"]
        ----
        import os

        print(os.environ["HOME"])
        ----
        """
    )

    expected = [
        '<div class="myblock"><div class="content"><div class="highlight"><pre><span></span><span class="hll">import os\n</span><span class="hll">\n</span><span class="hll">print(os.environ[&quot;HOME&quot;])\n</span></pre></div>\n</div></div>'
    ]

    _test(source, expected)


def test_source_highlights():
    source = textwrap.dedent(
        """
        [myblock, engine=source]
        ----
        import os:@:

        print(os.environ["HOME"]):@:
        ----
        """
    )

    expected = [
        '<div class="myblock"><div class="content"><div class="highlight"><pre><span></span><span class="hll">import os\n</span>\n<span class="hll">print(os.environ[&quot;HOME&quot;])\n</span></pre></div>\n</div></div>'
    ]

    _test(source, expected)


@patch("mau.visitors.html_visitor.highlight")
def test_source_block_definition(mock_highlight):
    mock_highlight.return_value = "XYXYXY"

    source = textwrap.dedent(
        """
        ::defblock:source, myblock, engine=source

        [source]
        ----
        import os

        print(os.environ["HOME"])
        ----
        """
    )

    expected = ['<div class="myblock"><div class="content">XYXYXY</div></div>']

    _test(source, expected)


@patch("mau.visitors.html_visitor.highlight")
def test_source_block_definition_variables_are_untouched(mock_highlight):
    mock_highlight.return_value = "XYXYXY"

    source = textwrap.dedent(
        """
        [source]
        ----
        a = 5

        print(f"{a}")
        ----
        """
    )

    expected = ['<div class="source"><div class="content">XYXYXY</div></div>']

    _test(source, expected)
