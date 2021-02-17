import textwrap

from unittest.mock import patch

from mau.parsers.main_parser import MainParser
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
        [source]
        ----
        import os

        print(os.environ["HOME"])
        ----
        """
    )

    expected = ['<div class="source"><div class="content">XYXYXY</div></div>']

    _test(source, expected)


@patch("mau.visitors.html_visitor.highlight")
def test_source_indentation(mock_highlight):
    mock_highlight.side_effect = lambda src, lexer, formatter: src

    source = textwrap.dedent(
        """
        [source,text]
        ----
        Not indented

            Indented
        ----
        """
    )

    expected = [
        '<div class="source"><div class="content">Not indented\n\n    Indented</div></div>'
    ]

    _test(source, expected)


def test_source_callouts():
    source = textwrap.dedent(
        """
        [source,callouts=":"]
        ----
        Some code:1:
        
        Some other code:3:
        ----
        1: This is the first line
        3: This is the second line
        """
    )

    expected = [
        """<div class="source"><div class="content"><div class="highlight"><pre><span></span>Some code <i class="conum" data-value="1"></i><b>(1)</b>\n\nSome other code <i class="conum" data-value="3"></i><b>(3)</b>\n</pre></div>\n</div></div><div class="colist arabic"><table><tbody><tr><td><i class="conum" data-value="1"></i><b>(1)</b></td><td>This is the first line</td></tr><tr><td><i class="conum" data-value="3"></i><b>(3)</b></td><td>This is the second line</td></tr></tbody></table></div>"""
    ]

    _test(source, expected)
