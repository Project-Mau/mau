import pytest

from mau.lexers.base_lexer import (
    Token,
    TokenTypes,
    TokenError,
    EOL,
    EOF,
    Text,
    Literal,
)
from mau.parsers.base_parser import BaseParser, ExpectedError

from tests.helpers import init_parser_factory

init_parser = init_parser_factory(BaseParser)


def test_initial_state():
    p = BaseParser()

    assert p.index == -1
    assert p.current_token == EOF


def test_load():
    p = init_parser("\n")

    assert p.index == -1
    assert p.current_token == EOF


def test_get_token_without_load():
    p = BaseParser()

    assert p.get_token() == EOF


def test_get_token():
    p = init_parser("\n")

    assert p.get_token() == EOL
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_tokens_contain_position():
    p = init_parser("\n")

    assert p.get_token().position == (0, 0)


def test_token_position_is_updated():
    p = init_parser("\n")

    assert p.get_token() == EOL
    assert p.get_token() == EOL
    assert p.get_token().position == (2, 0)


def test_get_token_after_eof():
    p = init_parser("\n")

    assert p.index == -1
    assert p.get_token() == EOL
    assert p.index == 0
    assert p.get_token() == EOL
    assert p.index == 1
    assert p.get_token() == EOF
    assert p.index == 2
    assert p.get_token() == EOF
    assert p.index == 3
    assert p.get_token() == EOF
    assert p.index == 3


def test_get_token_sets_current_token():
    p = init_parser("\n")

    p.get_token()
    assert p.current_token == EOL

    p.get_token()
    p.get_token()
    assert p.current_token == EOF


def test_get_token_value():
    p = init_parser("\n")

    assert p.get_token_value() is None


def test_get_token_accepts_type():
    p = init_parser("\n")

    assert p.get_token(TokenTypes.EOL) == EOL
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_get_token_accepts_type_and_value():
    p = init_parser("\n")

    assert p.get_token(TokenTypes.EOL, None) == EOL
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_get_token_checks_type():
    p = init_parser("\n")

    with pytest.raises(TokenError):
        p.get_token(TokenTypes.EOF)

    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_get_token_checks_type_and_value():
    p = init_parser("\n")

    with pytest.raises(TokenError):
        p.get_token(TokenTypes.EOL, "foobar")

    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_get_token_accepts_check_function():
    p = init_parser("\n")

    with pytest.raises(TokenError):
        p.get_token(TokenTypes.EOF, check=lambda x: x is not None)

    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_check_current_token():
    p = init_parser("\n")
    p.get_token()

    assert p.check_current_token(TokenTypes.EOL) == EOL

    # check_current_token doesn't advance the index
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_check_current_token_raises_exception():
    p = init_parser("\n")
    p.get_token()

    with pytest.raises(TokenError):
        p.check_current_token(TokenTypes.EOF)

    # check_current_token doesn't advance the index
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_check_current_token_value():
    p = init_parser("\n")
    p.get_token()

    assert p.check_current_token(TokenTypes.EOL, None) == EOL

    # check_current_token doesn't advance the index
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_check_current_token_with_function():
    p = init_parser("\n")
    p.get_token()

    assert p.check_current_token(TokenTypes.EOL, check=lambda x: x is None) == Token(
        TokenTypes.EOL
    )

    # check_current_token doesn't advance the index
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_peek_token():
    p = init_parser("\n")

    assert p.peek_token() == EOL
    assert p.get_token() == EOL
    assert p.get_token() == EOL
    assert p.peek_token() == EOF
    assert p.get_token() == EOF


def test_base_lexer_can_peek_more_than_available():
    p = init_parser("\n")

    assert p.get_token() == EOL
    assert p.get_token() == EOL
    assert p.get_token() == EOF
    assert p.peek_token() == EOF


def test_peek_token_checks_type():
    p = init_parser("\n")

    p.get_token()  # Get the first EOL
    p.get_token()  # Get the second EOL

    assert p.peek_token(TokenTypes.EOF) == EOF
    assert p.get_token() == EOF


def test_base_lexer_check_next_token_raises_exception():
    p = init_parser("\n")

    p.get_token()  # Get the first EOL
    p.get_token()  # Get the second EOL

    with pytest.raises(TokenError):
        p.peek_token(TokenTypes.EOL)

    # failed attempt doesn't advance the index
    assert p.get_token() == EOF


def test_peek_token_checks_type_and_value():
    p = init_parser("\n")

    with pytest.raises(TokenError):
        p.peek_token(TokenTypes.EOL, "foobar")

    assert p.get_token() == EOL
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_peek_token_accepts_check_function():
    p = init_parser("\n")

    with pytest.raises(TokenError):
        p.peek_token(TokenTypes.EOL, check=lambda x: x is not None)

    assert p.get_token() == EOL
    assert p.get_token() == EOL
    assert p.get_token() == EOF


def test_context_manager():
    p = init_parser("\n")

    with p:
        assert p.get_token() == EOL


def test_do_not_restore_status_if_no_error():
    p = init_parser("\n")

    with p:
        assert p.get_token(TokenTypes.EOL)
        assert p.get_token(TokenTypes.EOL)

    assert p.get_token(TokenTypes.EOF)


def test_restore_status_if_token_error():
    p = init_parser("\n")

    with p:
        assert p.get_token(TokenTypes.EOL)
        assert p.get_token(TokenTypes.EOL)
        assert p.get_token(TokenTypes.EOL)

    assert p.get_token(TokenTypes.EOL)
    assert p.get_token(TokenTypes.EOL)
    assert p.get_token(TokenTypes.EOF)


def test_context_manager_leaves_exceptions_untouched():
    p = init_parser("\n")

    with pytest.raises(ValueError):
        with p:
            raise ValueError


def test_token_error_can_be_raised():
    p = init_parser("\n")

    with p:
        assert p.get_token(TokenTypes.EOL)
        p.fail()

    assert p.get_token(TokenTypes.EOL)
    assert p.get_token(TokenTypes.EOL)
    assert p.get_token(TokenTypes.EOF)


def test_context_manager_nested():
    p = init_parser("\n")

    with p:
        p.get_token()
        with p:
            p.get_token(TokenTypes.EOF)

        p.get_token(TokenTypes.EOF)

    assert p.get_token(TokenTypes.EOL)
    assert p.get_token(TokenTypes.EOL)
    assert p.get_token(TokenTypes.EOF)


def test_context_manager_nested_with_success():
    p = init_parser("\n")

    with p:
        p.get_token()
        with p:
            p.get_token()
            # This succeeds
            p.get_token(TokenTypes.EOF)

        p.get_token(TokenTypes.EOL)

    assert p.get_token(TokenTypes.EOL)
    assert p.get_token(TokenTypes.EOL)
    assert p.get_token(TokenTypes.EOF)


def test_peek_token_is():
    p = init_parser("\n")

    p.get_token()  # Get the first EOL
    p.get_token()  # Get the second EOL

    assert p.peek_token_is(TokenTypes.EOL) is False
    assert p.peek_token_is(TokenTypes.EOF) is True


def test_force_token():
    p = init_parser("\n")

    assert p.force_token(TokenTypes.EOL) == EOL
    assert p.force_token(TokenTypes.EOL) == EOL

    with pytest.raises(ExpectedError):
        p.force_token(TokenTypes.EOL)


def test_force_token_in():
    p = init_parser("\n")

    p.force_token_in([EOL, EOF])
    p.get_token()  # Get the first EOL
    p.get_token()  # Get the second EOL

    with pytest.raises(ExpectedError):
        p.force_token_in([EOL])


def test_collect():
    p = init_parser("\n")

    tokens = p.collect([EOF])

    assert tokens == [EOL, EOL]

    tokens = p.collect([EOF])

    assert tokens == []


def test_collect_join():
    p = init_parser("\n")
    p.tokens = [
        Text("Some te"),
        Text("xt that will be joined"),
        Literal("!"),
        EOL,
        EOL,
    ]

    expected = "Some text that will be joined!"

    assert p.collect_join([EOF]) == expected


def test_collect_join_with_different_joiner():
    p = init_parser("\n")
    p.tokens = [
        Text("De-do-do"),
        Text("do"),
        EOL,
        EOL,
    ]

    expected = "De-do-do-do"

    assert p.collect_join([EOF], "-") == expected
