from unittest.mock import Mock, patch

import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.base_lexer import BaseLexer, TokenTypes
from mau.text_buffer.context import Context
from mau.text_buffer.text_buffer import TextBuffer
from mau.tokens.tokens import Token

from tests.helpers import dedent


def test_text_buffer_properties():
    mock_text_buffer = Mock()
    lex = BaseLexer(Environment())
    lex.text_buffer = mock_text_buffer

    assert lex._current_char == mock_text_buffer.current_char

    assert lex._current_line == mock_text_buffer.current_line

    assert lex._tail == mock_text_buffer.tail

    lex._nextline()
    mock_text_buffer.nextline.assert_called()

    lex._skip("four")
    mock_text_buffer.skip.assert_called_with(4)


def test_create_token():
    mock_text_buffer = Mock()
    lex = BaseLexer(Environment())
    lex.text_buffer = mock_text_buffer

    token = lex._create_token("sometype", "somevalue")
    assert token == Token("sometype", "somevalue")
    assert token.context == lex.text_buffer.context


@patch("mau.lexers.base_lexer.BaseLexer._nextline")
def test_create_tokens_from_line(mock_nextline):
    text_buffer = TextBuffer("Content")
    lex = BaseLexer(Environment())
    lex.text_buffer = text_buffer

    tokens = lex._create_tokens_from_line(TokenTypes.TEXT)

    assert tokens == [
        Token(TokenTypes.TEXT, "Content"),
        Token(TokenTypes.EOL),
    ]
    mock_nextline.assert_called()


def test_create_token_and_skip():
    mock_text_buffer = Mock()
    lex = BaseLexer(Environment())
    lex.text_buffer = mock_text_buffer
    lex._skip = Mock()

    token = lex._create_token_and_skip("sometype", "somevalue")
    assert token == Token("sometype", "somevalue")
    lex._skip.assert_called_with("somevalue")


def test_error():
    mock_text_buffer = Mock()
    lex = BaseLexer(Environment())
    lex.text_buffer = mock_text_buffer

    with pytest.raises(MauErrorException):
        lex._process_error()


def test_empty_text():
    lex = BaseLexer(Environment())
    lex.process(Mock())

    assert lex.tokens == [
        Token(TokenTypes.EOF),
    ]


def test_just_empty_lines():
    text_buffer = TextBuffer("\n")
    lex = BaseLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_lines_with_only_spaces():
    text_buffer = TextBuffer("    \n    ")
    lex = BaseLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_text():
    text = "Just simple text"
    text_buffer = TextBuffer(text)
    lex = BaseLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, text),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_multiple_lines():
    text = dedent(
        """
        This is text
        split into multiple lines

        with an empty line
        """
    )
    text_buffer = TextBuffer(text)
    lex = BaseLexer(Environment())
    lex.process(text_buffer)

    assert lex.tokens == [
        Token(TokenTypes.TEXT, "This is text"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.TEXT, "split into multiple lines"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOL),
        Token(TokenTypes.TEXT, "with an empty line"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.EOF),
    ]


def test_positions_default_context():
    text = dedent(
        """
        This is a line of text

        ---

        This is another line of text
        """
    )
    text_buffer = TextBuffer(text)
    lex = BaseLexer(Environment())
    lex.process(text_buffer)

    assert [i.context.asdict() for i in lex.tokens] == [
        {"column": 0, "line": 0, "source": None, "text": "This is a line of text"},
        {"column": 22, "line": 0, "source": None, "text": "This is a line of text"},
        {"column": 0, "line": 1, "source": None, "text": ""},
        {"column": 0, "line": 2, "source": None, "text": "---"},
        {"column": 3, "line": 2, "source": None, "text": "---"},
        {"column": 0, "line": 3, "source": None, "text": ""},
        {
            "column": 0,
            "line": 4,
            "source": None,
            "text": "This is another line of text",
        },
        {
            "column": 28,
            "line": 4,
            "source": None,
            "text": "This is another line of text",
        },
        {
            "column": 0,
            "line": 5,
            "source": None,
            "text": "",
        },
    ]


def test_positions():
    text = dedent(
        """
        This is a line of text

        ---

        This is another line of text
        """
    )
    text_buffer = TextBuffer(text, Context(line=42, column=123, source="main"))
    lex = BaseLexer(Environment())
    lex.process(text_buffer)

    assert [i.context.asdict() for i in lex.tokens] == [
        {"column": 123, "line": 42, "source": "main", "text": "This is a line of text"},
        {"column": 145, "line": 42, "source": "main", "text": "This is a line of text"},
        {"column": 123, "line": 43, "source": "main", "text": ""},
        {"column": 123, "line": 44, "source": "main", "text": "---"},
        {"column": 126, "line": 44, "source": "main", "text": "---"},
        {"column": 123, "line": 45, "source": "main", "text": ""},
        {
            "column": 123,
            "line": 46,
            "source": "main",
            "text": "This is another line of text",
        },
        {
            "column": 151,
            "line": 46,
            "source": "main",
            "text": "This is another line of text",
        },
        {
            "column": 123,
            "line": 47,
            "source": "main",
            "text": "",
        },
    ]
