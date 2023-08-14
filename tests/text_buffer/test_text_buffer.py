from mau.text_buffer.text_buffer import Context, TextBuffer

from tests.helpers import dedent


def test_text_buffer_current_line():
    text_buffer = TextBuffer("abcdef")

    assert text_buffer.current_line == "abcdef"


def test_text_buffer_current_line_goes_beyond_eof():
    text_buffer = TextBuffer("abcdef")
    text_buffer.line = 10

    assert text_buffer.current_line == ""


def test_text_buffer_current_char():
    text_buffer = TextBuffer("abcdef")

    assert text_buffer.current_char == "a"


def test_text_buffer_current_char_goes_beyond_eol():
    text_buffer = TextBuffer("abcdef")
    text_buffer.column = 10

    assert text_buffer.current_char == ""


def test_text_buffer_current_char_goes_beyond_eof():
    text_buffer = TextBuffer("abcdef")
    text_buffer.line = 10

    assert text_buffer.current_char == ""


def test_text_buffer_eof():
    text_buffer = TextBuffer("abcdef")

    text_buffer.line = 0
    assert text_buffer.eof is False

    text_buffer.line = 1
    assert text_buffer.eof is True

    text_buffer.line = 10
    assert text_buffer.eof is True


def test_text_buffer_eol():
    text_buffer = TextBuffer("abcdef", Context(source="main"))

    text_buffer.column = 0
    assert text_buffer.eol is False

    text_buffer.column = 6
    assert text_buffer.eol is True

    text_buffer.column = 10
    assert text_buffer.eol is True


def test_text_buffer_eof_eol_empty_file():
    text_buffer = TextBuffer("")

    assert text_buffer.eof is True
    assert text_buffer.eol is True


def test_text_buffer_peek_char():
    text_buffer = TextBuffer("abcdef")

    assert text_buffer.peek_char == "b"


def test_text_buffer_peek_char_goes_beyond_eol():
    text_buffer = TextBuffer("abcdef")
    text_buffer.column = 10

    assert text_buffer.peek_char == ""


def test_text_buffer_peek_char_goes_beyond_eof():
    text_buffer = TextBuffer("abcdef")
    text_buffer.line = 1

    assert text_buffer.peek_char == ""


def test_text_buffer_tail():
    text_buffer = TextBuffer("abcdefgh")
    text_buffer.column = 4

    assert text_buffer.tail == "efgh"


def test_text_buffer_tail_works_after_eol():
    text_buffer = TextBuffer("abcdefgh")
    text_buffer.column = 100

    assert text_buffer.tail == ""


def test_text_buffer_tail_works_after_eof():
    text_buffer = TextBuffer("abcdefgh")
    text_buffer.line = 10

    assert text_buffer.tail == ""


def test_text_buffer_nextline():
    text_buffer = TextBuffer("abc\ndef\nghi")
    text_buffer.nextline()

    assert text_buffer.line == 1
    assert text_buffer.column == 0


def test_text_buffer_nextline_last_line():
    text_buffer = TextBuffer("abc\ndef\nghi")
    text_buffer.line = 3
    text_buffer.column = 2
    text_buffer.nextline()

    assert text_buffer.line == 4
    assert text_buffer.column == 0


def test_text_buffer_position():
    text_buffer = TextBuffer()
    text_buffer.line = 1
    text_buffer.column = 3

    assert text_buffer.position == (1, 3)


def test_text_buffer_position_outext_bufferide():
    text_buffer = TextBuffer()
    text_buffer.line = 123
    text_buffer.column = 456

    assert text_buffer.position == (123, 456)


def test_text_buffer_set_position():
    text_buffer = TextBuffer()
    text_buffer.position = (222, 333)

    assert text_buffer.position == (222, 333)


def test_text_buffer_skip_defaults_to_one():
    text_buffer = TextBuffer("abc\ndef\nghi")
    text_buffer.skip()

    assert text_buffer.column == 1


def test_text_buffer_skip_accepts_value():
    text_buffer = TextBuffer("abc\ndef\nghi")
    text_buffer.skip(3)

    assert text_buffer.column == 3


def test_text_buffer_skip_can_go_beyond_eol():
    text_buffer = TextBuffer("abc\ndefghi")
    text_buffer.nextline()
    text_buffer.skip(25)

    assert text_buffer.column == 6


def test_text_buffer_default_context():
    text_buffer = TextBuffer(
        dedent(
            """
            Some text
            on multiple lines
            that I will use
            to check the context()
            """
        ),
    )

    text_buffer.position = (2, 6)

    assert text_buffer.context.asdict() == {
        "source": None,
        "text": "that I will use",
        "line": 2,
        "column": 6,
    }


def test_text_buffer_initial_context():
    text_buffer = TextBuffer(
        dedent(
            """
            Some text
            on multiple lines
            that I will use
            to check the context()
            """
        ),
        Context(72, 123, "main"),
    )

    assert text_buffer.current_line == "Some text"
    assert text_buffer.line == 0
    assert text_buffer.column == 0
    assert text_buffer.context.asdict() == {
        "source": "main",
        "text": "Some text",
        "line": 72,
        "column": 123,
    }
