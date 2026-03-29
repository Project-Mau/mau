import textwrap
from unittest.mock import Mock, patch

import pytest

from mau.environment.environment import Environment
from mau.lexers.base_lexer import (
    BaseLexer,
    rematch,
)
from mau.message import MauException, MauMessageType
from mau.test_helpers import (
    TEST_CONTEXT_SOURCE,
    NullMessageHandler,
    compare_asdict_list,
    dedent,
    generate_context,
    init_lexer_factory,
    lexer_runner_factory,
)
from mau.text_buffer import TextBuffer
from mau.token import Token, TokenType

init_lexer = init_lexer_factory(BaseLexer)

runner = lexer_runner_factory(BaseLexer)


@patch("mau.lexers.base_lexer.re")
def test_rematch(mock_re):
    mock_regexp = Mock()
    mock_text = Mock()

    rematch(mock_regexp, mock_text)

    mock_re.match.assert_called_with(mock_regexp, mock_text)


def test_text_buffer_properties():
    mock_text_buffer = Mock()
    test_environment = Environment()

    lex = BaseLexer(
        mock_text_buffer,
        NullMessageHandler(),
        test_environment,
    )

    assert lex.text_buffer == mock_text_buffer
    assert lex.tokens == []
    assert lex.environment == test_environment

    assert lex._current_char == mock_text_buffer.current_char
    assert lex._current_line == mock_text_buffer.current_line
    assert lex._position == mock_text_buffer.position
    assert lex._tail == mock_text_buffer.tail

    lex._nextline()
    mock_text_buffer.nextline.assert_called()

    lex._skip("sometext")
    mock_text_buffer.skip.assert_called_with(8)


def test_create_token_and_skip():
    text_buffer = TextBuffer("somevalue", source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    token = lex._create_token_and_skip(TokenType.TEXT, "somevalue")

    assert token == Token(TokenType.TEXT, "somevalue", generate_context(0, 0, 0, 9))


def test_create_token_and_skip_with_no_value():
    text_buffer = TextBuffer("somevalue", source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    token = lex._create_token_and_skip(TokenType.TEXT)

    assert token == Token(TokenType.TEXT, "", generate_context(0, 0, 0, 0))


def test_create_token_and_skip_with_value_none():
    text_buffer = TextBuffer("somevalue", source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    token = lex._create_token_and_skip(TokenType.TEXT, None)

    assert token == Token(TokenType.TEXT, "", generate_context(0, 0, 0, 0))


def test_process_error():
    mock_text_buffer = Mock()
    lex = BaseLexer(
        mock_text_buffer,
        NullMessageHandler(),
    )

    with pytest.raises(MauException) as exc:
        lex._process_error()

    assert exc.value.message.type == MauMessageType.ERROR_LEXER
    assert exc.value.message.text == "Cannot process token."


def test_process_eof_if_true():
    text_buffer = TextBuffer("", source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_eof()

    compare_asdict_list(
        tokens,
        [
            Token(TokenType.EOF, "", generate_context(0, 0, 0, 0)),
        ],
    )


def test_process_eof_if_false():
    text_buffer = TextBuffer("somevalue", source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_eof()

    assert tokens is None


def test_process_empty_line_empty():
    test_text = ""
    text_buffer = TextBuffer(test_text, source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_empty_line()

    compare_asdict_list(
        tokens,
        [
            Token(TokenType.EOL, test_text, generate_context(0, 0, 0, 0)),
        ],
    )
    assert lex._position == (1, 0)


def test_process_empty_line_with_spaces():
    test_text = "   "
    text_buffer = TextBuffer(test_text, source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_empty_line()

    compare_asdict_list(
        tokens,
        [
            Token(TokenType.EOL, test_text, generate_context(0, 0, 0, len(test_text))),
        ],
    )
    assert lex._position == (1, 0)


def test_process_empty_line_not_empty():
    test_text = "sometext"
    text_buffer = TextBuffer(test_text, source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_empty_line()

    assert tokens is None
    assert lex._position == (0, 0)


def test_process_trailing_spaces():
    test_text = "sometext   "
    text_buffer = TextBuffer(test_text, source_filename=TEST_CONTEXT_SOURCE)

    # This skips the text.
    text_buffer.column = 8

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_trailing_spaces()

    compare_asdict_list(tokens, [])
    assert lex._position == (1, 0)


def test_process_trailing_spaces_no_spaces():
    test_text = "sometext"
    text_buffer = TextBuffer(test_text, source_filename=TEST_CONTEXT_SOURCE)

    # This skips the text.
    text_buffer.column = 8

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_trailing_spaces()

    compare_asdict_list(tokens, [])
    assert lex._position == (1, 0)


def test_process_trailing_spaces_not_eol():
    test_text = "sometext  more text"
    text_buffer = TextBuffer(test_text, source_filename=TEST_CONTEXT_SOURCE)

    # This skips the first word.
    # There are spaces but also
    # more words.
    text_buffer.column = 8

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_trailing_spaces()

    assert tokens is None
    assert lex._position == (0, 8)


def test_process_text():
    test_text = "sometext"
    text_buffer = TextBuffer(test_text, source_filename=TEST_CONTEXT_SOURCE)

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_text()

    compare_asdict_list(
        tokens,
        [
            Token(TokenType.TEXT, "sometext", generate_context(0, 0, 0, 8)),
        ],
    )
    assert lex._position == (1, 0)


def test_process_text_just_tail():
    test_text = "sometext and more text"
    text_buffer = TextBuffer(test_text, source_filename=TEST_CONTEXT_SOURCE)

    # This skips the initial word
    text_buffer.column = 8

    lex = BaseLexer(
        text_buffer,
        NullMessageHandler(),
    )
    tokens = lex._process_text()

    compare_asdict_list(
        tokens,
        [
            Token(TokenType.TEXT, " and more text", generate_context(0, 8, 0, 22)),
        ],
    )
    assert lex._position == (1, 0)


def test_run_empty_text():
    lex = runner("")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.EOF, "", generate_context(0, 0, 0, 0)),
        ],
    )


def test_empty_lines():
    lex = runner("\n")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.EOL, "", generate_context(0, 0, 0, 0)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_lines_with_only_spaces():
    lex = runner("      \n      ")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.EOL, "", generate_context(0, 0, 0, 0)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_text():
    lex = runner("Just simple text")

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Just simple text", generate_context(0, 0, 0, 16)),
            Token(TokenType.EOF, "", generate_context(1, 0, 1, 0)),
        ],
    )


def test_multiple_lines():
    text = dedent(
        """
        This is text
        split into multiple lines

        with an empty line
        """
    )
    lex = runner(text)

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "This is text", generate_context(0, 0, 0, 12)),
            Token(
                TokenType.TEXT,
                "split into multiple lines",
                generate_context(1, 0, 1, 25),
            ),
            Token(TokenType.EOL, "", generate_context(2, 0, 2, 0)),
            Token(TokenType.TEXT, "with an empty line", generate_context(3, 0, 3, 18)),
            Token(TokenType.EOF, "", generate_context(4, 0, 4, 0)),
        ],
    )


def test_text_buffer_offset():
    source = "Just simple text"

    text_buffer = TextBuffer(
        textwrap.dedent(source),
        start_line=11,
        start_column=22,
        source_filename=TEST_CONTEXT_SOURCE,
    )

    lex = init_lexer(text_buffer)
    lex.process()

    compare_asdict_list(
        lex.tokens,
        [
            Token(TokenType.TEXT, "Just simple text", generate_context(11, 22, 11, 38)),
            Token(TokenType.EOF, "", generate_context(12, 0, 12, 0)),
        ],
    )
