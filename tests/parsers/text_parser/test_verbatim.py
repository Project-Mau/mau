from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import TextNode, VerbatimNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_verbatim():
    source = "`Many different words`"

    expected = [
        VerbatimNode("Many different words"),
    ]

    assert runner(source).nodes == expected


def test_verbatim_escaped_backtick():
    source = r"`\``"

    expected = [
        VerbatimNode("`"),
    ]

    assert runner(source).nodes == expected


def test_verbatim_style_inside_verbatim():
    source = r"`_Many different words_`"

    expected = [
        VerbatimNode("_Many different words_"),
    ]

    assert runner(source).nodes == expected


def test_verbatim_open():
    source = r"`Many different words"

    expected = [
        TextNode("`Many different words"),
    ]

    assert runner(source).nodes == expected


def test_verbatim_escape_characters():
    source = r"`$Many$ %different% \words`"

    expected = [
        VerbatimNode(r"$Many$ %different% \words"),
    ]

    assert runner(source).nodes == expected
