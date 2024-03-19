from unittest.mock import Mock

import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.base_lexer import BaseLexer, TokenTypes
from mau.parsers.base_parser import BaseParser, TokenError
from mau.tokens.tokens import Token

from tests.helpers import init_parser_factory

init_parser = init_parser_factory(BaseLexer, BaseParser)


def test_save():
    parser = BaseParser(Environment())
    node = Mock()
    parser._save(node)

    assert parser.nodes == [node]


def test_initial_state():
    parser = BaseParser(Environment())
    parser.tokens = [Token(TokenTypes.EOF)]

    assert parser.index == -1
    assert parser._current_token == Token(TokenTypes.EOF)


def test_load():
    parser = init_parser("\n")

    assert parser.index == -1
    assert parser._current_token == Token(TokenTypes.EOF)


def test_get_token_without_load():
    parser = BaseParser(Environment())
    parser.tokens = [Token(TokenTypes.EOF)]

    assert parser._get_token() == Token(TokenTypes.EOF)


def test_get_token():
    parser = init_parser("")

    assert parser._get_token() == Token(TokenTypes.EOF)


def test_put_token():
    parser = init_parser("")

    parser._put_token(Token(TokenTypes.LITERAL, "*"))
    assert parser._get_token() == Token(TokenTypes.LITERAL, "*")
    assert parser._get_token() == Token(TokenTypes.EOF)


def test_get_token_after_eof():
    parser = init_parser("")

    assert parser.index == -1

    assert parser._get_token() == Token(TokenTypes.EOF)
    assert parser.index == 0

    assert parser._get_token() == Token(TokenTypes.EOF)
    assert parser.index == 1

    assert parser._get_token() == Token(TokenTypes.EOF)
    assert parser.index == 1


def test_get_token_sets_current_token():
    parser = init_parser("Some text\nSome other text")

    assert parser._get_token() == Token(TokenTypes.TEXT, "Some text")
    assert parser._current_token == Token(TokenTypes.TEXT, "Some text")

    assert parser._get_token() == Token(TokenTypes.EOL)
    assert parser._current_token == Token(TokenTypes.EOL)

    assert parser._get_token() == Token(TokenTypes.TEXT, "Some other text")
    assert parser._current_token == Token(TokenTypes.TEXT, "Some other text")


def test_get_token_accepts_type():
    parser = init_parser("Some text\nSome other text")

    assert parser._get_token(TokenTypes.TEXT) == Token(TokenTypes.TEXT, "Some text")


def test_get_token_accepts_type_and_value():
    parser = init_parser("Some text\nSome other text")

    assert parser._get_token(TokenTypes.TEXT, "Some text") == Token(
        TokenTypes.TEXT, "Some text"
    )


def test_get_token_checks_type():
    parser = init_parser("Some text\nSome other text")

    with pytest.raises(TokenError):
        parser._get_token(TokenTypes.EOL)


def test_get_token_checks_type_and_value():
    parser = init_parser("Some text\nSome other text")

    with pytest.raises(TokenError):
        parser._get_token(TokenTypes.TEXT, "foobar")


def test_get_token_accepts_check_function():
    parser = init_parser("Some text\nSome other text")

    with pytest.raises(TokenError):
        parser._get_token(TokenTypes.TEXT, check=lambda x: x == "foobar")


def test_check_current_token():
    parser = init_parser("Some text\nSome other text")

    parser._get_token()

    assert parser._check_current_token(TokenTypes.TEXT) == Token(
        TokenTypes.TEXT, "Some text"
    )

    # check_current_token doesn't advance the index
    assert parser._get_token() == Token(TokenTypes.EOL)


def test_check_current_token_raises_exception():
    parser = init_parser("Some text\nSome other text")

    parser._get_token()

    with pytest.raises(TokenError):
        parser._check_current_token(TokenTypes.EOF)


def test_check_current_token_value():
    parser = init_parser("Some text\nSome other text")

    parser._get_token()

    assert parser._check_current_token(TokenTypes.TEXT, "Some text") == Token(
        TokenTypes.TEXT, "Some text"
    )


def test_check_current_token_with_function():
    parser = init_parser("Some text\nSome other text")

    parser._get_token()

    assert parser._check_current_token(
        TokenTypes.TEXT, check=lambda x: x == "Some text"
    ) == Token(TokenTypes.TEXT, "Some text")


def test_peek_token():
    parser = init_parser("Some text\nSome other text")

    assert parser._peek_token() == Token(TokenTypes.TEXT, "Some text")
    assert parser._get_token() == Token(TokenTypes.TEXT, "Some text")
    assert parser._get_token() == Token(TokenTypes.EOL)
    assert parser._get_token() == Token(TokenTypes.TEXT, "Some other text")
    assert parser._peek_token() == Token(TokenTypes.EOL)
    assert parser._get_token() == Token(TokenTypes.EOL)
    assert parser._peek_token() == Token(TokenTypes.EOF)
    assert parser._get_token() == Token(TokenTypes.EOF)


def test_base_lexer_can_peek_after_eof():
    parser = init_parser("Some text\nSome other text")

    assert parser._get_token() == Token(TokenTypes.TEXT, "Some text")
    assert parser._get_token() == Token(TokenTypes.EOL)
    assert parser._get_token() == Token(TokenTypes.TEXT, "Some other text")
    assert parser._get_token() == Token(TokenTypes.EOL)
    assert parser._get_token() == Token(TokenTypes.EOF)
    assert parser._peek_token() == Token(TokenTypes.EOF)


def test_peek_token_checks_type():
    parser = init_parser("Some text\nSome other text")

    assert parser._peek_token(TokenTypes.TEXT) == Token(TokenTypes.TEXT, "Some text")


def test_base_lexer_check_next_token_raises_exception():
    parser = init_parser("Some text\nSome other text")

    with pytest.raises(TokenError):
        parser._peek_token(TokenTypes.EOL)

    # failed attempt doesn't advance the index
    assert parser._get_token() == Token(TokenTypes.TEXT, "Some text")


def test_peek_token_checks_type_and_value():
    parser = init_parser("Some text\nSome other text")

    with pytest.raises(TokenError):
        parser._peek_token(TokenTypes.EOL, "foobar")


def test_peek_token_accepts_check_function():
    parser = init_parser("Some text\nSome other text")

    parser._peek_token(TokenTypes.TEXT, check=lambda x: x == "Some text")

    with pytest.raises(TokenError):
        parser._peek_token(TokenTypes.TEXT, check=lambda x: x == "Some other text")


def test_context_manager():
    parser = init_parser("Some text\nSome other text")

    with parser:
        assert parser._get_token() == Token(TokenTypes.TEXT, "Some text")


def test_do_not_restore_status_if_no_error():
    parser = init_parser("Some text\nSome other text")

    with parser:
        assert parser._get_token(TokenTypes.TEXT, "Some text")
        assert parser._get_token(TokenTypes.EOL)
        assert parser._get_token(TokenTypes.TEXT, "Some other text")
        assert parser._get_token(TokenTypes.EOL)

    assert parser._get_token(TokenTypes.EOF)


def test_restore_status_if_token_error():
    parser = init_parser("Some text\nSome other text")

    with parser:
        assert parser._get_token(TokenTypes.TEXT, "Some text")
        assert parser._get_token(TokenTypes.TEXT, "Some other text")
        assert parser._get_token(TokenTypes.TEXT, "Some final text")

    assert parser._get_token(TokenTypes.TEXT, "Some text")


def test_context_manager_leaves_exceptions_untouched():
    parser = init_parser("Some text\nSome other text")

    with pytest.raises(ValueError):
        with parser:
            raise ValueError


def test_token_error_can_be_raised():
    parser = init_parser("Some text\nSome other text")

    with parser:
        assert parser._get_token(TokenTypes.TEXT, "Some text")
        raise TokenError

    assert parser._get_token(TokenTypes.TEXT, "Some text")


def test_context_manager_nested_success():
    parser = init_parser("Some text\nSome other text")

    with parser:
        parser._get_token(TokenTypes.TEXT, "Some text")
        parser._get_token(TokenTypes.EOL)
        with parser:
            parser._get_token(TokenTypes.TEXT, "Some other text")
            parser._get_token(TokenTypes.EOL)

        parser._get_token(TokenTypes.EOF)

    assert parser._get_token(TokenTypes.EOF)


def test_context_manager_nested_failure():
    parser = init_parser("Some text\nSome other text")

    with parser:
        parser._get_token(TokenTypes.TEXT, "Some text")
        parser._get_token(TokenTypes.EOL)
        with parser:
            parser._get_token(TokenTypes.TEXT, "Some text")

        parser._get_token(TokenTypes.TEXT, "Some other text")
        parser._get_token(TokenTypes.EOL)

    assert parser._get_token(TokenTypes.EOF)


def test_peek_token_is():
    parser = init_parser("Some text\nSome other text")

    assert parser._peek_token_is(TokenTypes.EOL) is False
    assert parser._peek_token_is(TokenTypes.TEXT) is True


def test_force_token():
    parser = init_parser("Some text\nSome other text")

    assert parser._force_token(TokenTypes.TEXT) == Token(TokenTypes.TEXT, "Some text")
    assert parser._force_token(TokenTypes.EOL) == Token(TokenTypes.EOL)
    assert parser._force_token(TokenTypes.TEXT) == Token(
        TokenTypes.TEXT, "Some other text"
    )

    with pytest.raises(MauErrorException):
        parser._force_token(TokenTypes.TEXT)


def test_collect():
    parser = init_parser("Some text\nSome other text")

    tokens = parser._collect([Token(TokenTypes.EOF)])

    assert tokens == [
        Token(TokenTypes.TEXT, "Some text"),
        Token(TokenTypes.EOL),
        Token(TokenTypes.TEXT, "Some other text"),
        Token(TokenTypes.EOL),
    ]

    tokens = parser._collect([Token(TokenTypes.EOF)])

    assert tokens == []


def test_collect_join():
    parser = init_parser("Some te\nxt that will be joined\n!")

    expected = "Some text that will be joined!"

    assert parser._collect_join([Token(TokenTypes.EOF)]) == expected


def test_collect_join_with_different_joiner():
    parser = init_parser("Some te\nxt that will be joined\n!")

    expected = "Some te-xt that will be joined-!"

    assert parser._collect_join([Token(TokenTypes.EOF)], "-") == expected


def test_collect_escapes_are_kept():
    parser = init_parser("")
    parser.tokens = [
        Token(TokenTypes.TEXT, "Some text"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.TEXT, "Some other text"),
        Token(TokenTypes.EOF),
    ]

    tokens = parser._collect([Token(TokenTypes.EOF)])

    assert tokens == [
        Token(TokenTypes.TEXT, "Some text"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.TEXT, "Some other text"),
    ]


def test_collect_escape_stop_tokens_are_removed():
    parser = init_parser("")
    parser.tokens = [
        Token(TokenTypes.TEXT, "Some text"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "["),
    ]

    tokens = parser._collect([Token(TokenTypes.LITERAL, "[")])

    assert tokens == [
        Token(TokenTypes.TEXT, "Some text"),
        Token(TokenTypes.LITERAL, "["),
    ]


def test_collect_escape_stop_tokens_are_removed2():
    parser = init_parser("")
    parser.tokens = [
        Token(TokenTypes.TEXT, "Some text"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "["),
    ]

    tokens = parser._collect(
        [Token(TokenTypes.LITERAL, "[")], preserve_escaped_stop_tokens=True
    )

    assert tokens == [
        Token(TokenTypes.TEXT, "Some text"),
        Token(TokenTypes.LITERAL, "\\"),
        Token(TokenTypes.LITERAL, "["),
    ]


def test_error():
    parser = init_parser("Some text")

    parser._get_token()
    parser._get_token()

    with pytest.raises(MauErrorException) as exception:
        parser._error()


def test_error_with_message():
    parser = init_parser("Some text")

    parser._get_token()
    parser._get_token()

    with pytest.raises(MauErrorException) as exception:
        parser._error("Some message")

    assert exception.value.error.message == "Some message"


def test_unknown_token():
    parser = BaseParser(Environment())

    with pytest.raises(MauErrorException) as exception:
        parser.parse([Token("UNKNOWN")])

    assert exception.value.error.message == "Cannot parse token"
