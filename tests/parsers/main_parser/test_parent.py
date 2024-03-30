from mau.lexers.main_lexer import MainLexer
from mau.parsers.main_parser import MainParser

from tests.helpers import parser_runner_factory

mainrunner = parser_runner_factory(MainLexer, MainParser)


def test_parent_block():
    source = """
    ----
    Content
    ----
    """

    nodes = mainrunner(source).nodes

    block_node = nodes[0]
    paragraph_node = block_node.children[0]

    assert paragraph_node.parent is block_node


def test_parent_paragraph():
    source = "Some text _and style_ and *more style* here"

    nodes = mainrunner(source).nodes

    paragraph_node = nodes[0]
    text_node = paragraph_node.children[0]
    style_node = paragraph_node.children[1]

    assert text_node.parent is paragraph_node
    assert style_node.parent is paragraph_node
