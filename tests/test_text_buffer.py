import textwrap

import pytest

from mau import text_buffer


def dedent(text):
    return textwrap.dedent(text).strip()


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
        textwrap.dedent(
            """
            Some text
            on multiple lines
            that I will use
            to check the context()
            """
        )
    )

    context = dedent(
        """
        2: on multiple lines
        3: that I will use
                  ^
        """
    )

    assert tb.context(3, 7) == context.split("\n")


def test_context_pair_line_numbers():
    tb = text_buffer.TextBuffer(
        textwrap.dedent(
            """
            Some text
            on multiple lines
            that I will use
            to check the context()
            and to text that
            the whole thing
            works with bigger
            line numbers
            in front of the lines
            I need to add
            more text
            """
        )
    )

    context = dedent(
        """
        09: in front of the lines
        10: I need to add
                   ^
        """
    )

    assert tb.context(10, 7) == context.split("\n")


def test_context_long_lines():
    tb = text_buffer.TextBuffer(
        textwrap.dedent(
            """
            Some text on multiple lines that I will use to check the context() and to text that the whole thing
            works with bigger line numbers in front of the lines I need to add more text
            """
        )
    )

    context = dedent(
        """
        1: [...] e lines that I will use to check the cont [...]
        2: [...] ne numbers in front of the lines I need t [...]
                                     ^
        """
    )

    assert tb.context(2, 40) == context.split("\n")


def test_context_long_lines_beginning():
    tb = text_buffer.TextBuffer(
        textwrap.dedent(
            """
            Some text on multiple lines that I will use to check the context() and to text that the whole thing
            works with bigger line numbers in front of the lines I need to add more text
            """
        )
    )

    context = dedent(
        """
        1: Some text on multiple lines that I will [...]
        2: works with bigger line numbers in front [...]
                             ^
        """
    )

    assert tb.context(2, 18) == context.split("\n")


def test_context_long_lines_end():
    tb = text_buffer.TextBuffer(
        textwrap.dedent(
            """
            Some text on multiple lines that I will use to check the context() and to text that the whole thing
            works with bigger line numbers in front of the lines I need to add more text
            """
        )
    )

    context = dedent(
        """
        1: [...] use to check the context() and to text th [...]
        2: [...] of the lines I need to add more text
                                     ^
        """
    )

    assert tb.context(2, 60) == context.split("\n")
