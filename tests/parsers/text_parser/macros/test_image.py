from mau.lexers.text_lexer import TextLexer
from mau.nodes.macros import MacroImageNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_macro_image():
    source = "[image](/the/path.jpg)"

    expected = [
        MacroImageNode("/the/path.jpg"),
    ]

    assert runner(source).nodes == expected


def test_macro_image_with_alt_text():
    source = '[image](/the/path.jpg,"alt name")'

    expected = [
        MacroImageNode("/the/path.jpg", alt_text="alt name"),
    ]

    assert runner(source).nodes == expected


def test_macro_image_with_width_and_height():
    source = "[image](/the/path.jpg,width=1200,height=600)"

    expected = [
        MacroImageNode("/the/path.jpg", alt_text=None, width="1200", height="600"),
    ]

    assert runner(source).nodes == expected
