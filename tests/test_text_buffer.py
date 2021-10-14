import textwrap

import pytest

from tests.helpers import dedent

from mau import text_buffer


def test_text_buffer_init_empty():
    tb = text_buffer.TextBuffer()

    with pytest.raises(text_buffer.EOFError):
        tb.current_char


def test_text_buffer_init_one_line():
    tb = text_buffer.TextBuffer("abcdef")

    assert tb.current_char == "a"
    assert tb.peek_char == "b"
    assert tb.current_line == "abcdef"
    assert tb.line == 0
    assert tb.column == 0


def test_text_buffer_end_of_line_peek_char():
    tb = text_buffer.TextBuffer("abcdef")
    tb.column = 5

    assert tb.current_char == "f"
    with pytest.raises(text_buffer.EOLError):
        tb.peek_char


def test_text_buffer_end_of_line_current_char():
    tb = text_buffer.TextBuffer("abcdef")
    tb.column = 200

    with pytest.raises(text_buffer.EOLError):
        tb.current_char


def test_text_buffer_error_at_end_of_file():
    tb = text_buffer.TextBuffer("abcdef")
    tb.line = 1

    with pytest.raises(text_buffer.EOFError):
        tb.current_line


def test_text_buffer_error_after_end_of_file():
    tb = text_buffer.TextBuffer("abcdef")
    tb.line = 100

    with pytest.raises(text_buffer.EOFError):
        tb.current_line


def test_text_buffer_tail():
    ts = text_buffer.TextBuffer("abcdefgh")
    ts.column = 4

    assert ts.tail == "efgh"


def test_text_buffer_multiple_lines():
    tb = text_buffer.TextBuffer("abc\ndef\nghi")
    tb.line = 1
    tb.column = 1

    assert tb.current_line == "def"
    assert tb.current_char == "e"
    assert tb.peek_char == "f"


def test_text_buffer_nextline():
    tb = text_buffer.TextBuffer("abc\ndef\nghi")
    tb.line = 1
    tb.column = 2
    tb.nextline()

    assert tb.position == (2, 0)


def test_text_buffer_position():
    tb = text_buffer.TextBuffer()
    tb.line = 123
    tb.column = 456

    assert tb.position == (123, 456)


def test_text_buffer_set_position():
    tb = text_buffer.TextBuffer()
    tb.position = (222, 333)

    assert tb.position == (222, 333)


def test_text_buffer_skip_defaults_to_one():
    tb = text_buffer.TextBuffer("abc\ndef\nghi")
    tb.skip()

    assert tb.column == 1


def test_text_buffer_skip_accepts_value():
    tb = text_buffer.TextBuffer("abc\ndef\nghi")
    tb.skip(3)

    assert tb.column == 3


def test_text_buffer_goto():
    tb = text_buffer.TextBuffer()
    tb.goto(12, 45)

    assert tb.position == (12, 45)


def test_text_buffer_goto_default_column():
    tb = text_buffer.TextBuffer()
    tb.goto(12)

    assert tb.position == (12, 0)


def test_context():
    tb = text_buffer.TextBuffer(
        dedent(
            """
            Some text
            on multiple lines
            that I will use
            to check the context()
            """
        )
    )

    assert tb.context(2, 7) == {
        "text": [
            "2: that I will use",
            "          ^",
        ],
        "line": 2,
        "column": 7,
    }


def test_context_long_line_center():
    tb = text_buffer.TextBuffer(
        dedent(
            """
            Some text on a very long line that I will use to check the context() and to test that the whole thing works
            """
        )
    )

    assert tb.context(0, 50) == {
        "text": [
            "0: [...]y long line that I will use to check the context() and to test th[...]",
            "                                        ^",
        ],
        "line": 0,
        "column": 50,
    }


def test_context_long_line_beginning():
    tb = text_buffer.TextBuffer(
        dedent(
            """
            Some text on a very long line that I will use to check the context() and to test that the whole thing works
            """
        )
    )

    assert tb.context(0, 30) == {
        "text": [
            "0: Some text on a very long line that I will use to check the cont[...]",
            "                                 ^",
        ],
        "line": 0,
        "column": 30,
    }


def test_context_long_line_end():
    tb = text_buffer.TextBuffer(
        dedent(
            """
            Some text on a very long line that I will use to check the context() and to test that the whole thing works
            """
        )
    )

    assert tb.context(0, 100) == {
        "text": [
            "0: [...] and to test that the whole thing works",
            "                                        ^",
        ],
        "line": 0,
        "column": 100,
    }


def test_text_buffer_insert():
    tb = text_buffer.TextBuffer("abc\ndef\nghi")
    tb.line = 1
    tb.column = 0

    tb.insert("XYZ\n")

    assert tb.current_line == "XYZ"
    assert tb.position == (1, 0)
    tb.nextline()
    assert tb.current_line == "def"
    assert tb.position == (2, 0)
