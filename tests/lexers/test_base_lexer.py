import pytest

from mau import text_buffer
from mau.lexers.base_lexer import BaseLexer, LexerError, EOL, EOF, Text, WS


def test_no_text():
    lex = BaseLexer()

    lex.process("")

    assert lex.tokens == [EOL, EOF]


def test_empty_lines():
    lex = BaseLexer()

    lex.process("\n")

    assert lex.tokens == [EOL, EOL, EOF]
    assert [t.position for t in lex.tokens] == [
        (0, 0),
        (1, 0),
        (2, 0),
    ]


def test_initial_position():
    lex = BaseLexer(initial_position=(1, 5))

    lex.process("\n")

    assert lex.tokens == [EOL, EOL, EOF]
    assert [t.position for t in lex.tokens] == [
        (1, 5),
        (2, 0),
        (3, 0),
    ]


def test_process_letters():
    lex = BaseLexer()

    lex.process("abcd")

    assert lex.tokens == [Text("a"), Text("b"), Text("c"), Text("d"), EOL, EOF]
    assert [t.position for t in lex.tokens] == [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (1, 0),
    ]


def test_process_whitespace():
    lex = BaseLexer()

    lex.process("a   b")

    assert lex.tokens == [Text("a"), WS("   "), Text("b"), EOL, EOF]


def test_lexer_error():
    lex = BaseLexer()

    with pytest.raises(LexerError):
        lex.process("123")


####################################################
# Private methods
#
# These normally shouldn't be tested, but this class
# is the foundation of all other lexers, so I prefer
# to keep an eye on the internal methods, as they
# will be used by the child lexers.


def test_wrap():
    lex = BaseLexer()

    assert lex._wrap(None) is None
    assert lex._wrap([5, 6]) == [5, 6]
    assert lex._wrap(5) == [5]


def test_current_char_and_line():
    lex = BaseLexer()
    buf = text_buffer.TextBuffer()
    buf.load("Just an example\nOn two lines")
    lex._text_buffer = buf

    assert lex._current_char == "J"
    assert lex._current_line == "Just an example"
