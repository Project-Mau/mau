from mau.lexers.main_lexer import MainLexer
from mau.lexers.text_lexer import TextLexer
from mau.parsers.main_parser import MainParser
from mau.parsers.text_parser import TextParser

from tests.helpers import parser_runner_factory

mainrunner = parser_runner_factory(MainLexer, MainParser)
textrunner = parser_runner_factory(TextLexer, TextParser)


def test_parent_block():
    source = """
    ----
    Content
    ----
    """

    nodes = mainrunner(source).nodes

    block_node = nodes[0]
    paragraph_node = block_node.content[0]

    assert paragraph_node.parent is block_node


# def test_parent_paragraph():
#     source = "Some text _and style_ and *more style* here"

#     nodes = textrunner(source).nodes

#     sentence_node = nodes[0]
#     text_node = sentence_node.content[0]
#     style_node = sentence_node.content[1]

#     assert text_node.parent is sentence_node
#     assert style_node.parent is sentence_node
