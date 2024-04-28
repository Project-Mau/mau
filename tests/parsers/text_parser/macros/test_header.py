from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import TextNode
from mau.nodes.macros import MacroHeaderNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_macro_header():
    source = '[header](id, "link text")'

    node = MacroHeaderNode("id", children=[TextNode("link text")])

    parser = runner(source)
    assert parser.nodes == [node]
    assert parser.links == [node]


def test_macro_header_without_text():
    source = "[header](id)"

    node = MacroHeaderNode("id", children=[])

    parser = runner(source)
    assert parser.nodes == [node]
    assert parser.links == [node]
