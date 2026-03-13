from unittest.mock import Mock

import pytest

from mau.environment.environment import Environment
from mau.lexers.base_lexer import BaseLexer
from mau.message import MauException, MauMessageType
from mau.parsers.base_parser import (
    BaseParser,
)
from mau.parsers.managers.tokens_manager import TokenError
from mau.test_helpers import (
    generate_context,
    init_parser_factory,
)
from mau.token import Token, TokenType

init_parser = init_parser_factory(BaseLexer, BaseParser)


def test_save():
    parent_node = Mock()
    node = Mock()
    parser = BaseParser([], Environment(), parent_node=parent_node)

    parser._save(node)

    assert parser.nodes == [node]
    node.set_parent.assert_called_with(parent_node)


def test_unknown_token():
    test_context = generate_context(0, 0, 0, 0)
    test_token = Token(TokenType.EOL, "", test_context)

    parser = BaseParser([test_token], Environment())

    with pytest.raises(MauException) as exc:
        parser.parse()

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Cannot parse token."
    assert exc.value.message.context == generate_context(0, 0, 0, 0)


def test_process_functions_token_error():
    process_test = Mock()
    process_test.side_effect = TokenError

    def process_functions():
        return [process_test]

    test_context = generate_context(0, 0, 0, 0)
    test_token = Token(TokenType.EOL, "", test_context)

    parser = BaseParser([test_token], Environment())
    parser._process_functions = process_functions

    with pytest.raises(MauException) as exc:
        parser.parse()

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Cannot parse token."
    process_test.assert_called()


def test_process_functions_success():
    process_test = Mock()
    process_test.return_value = True

    def process_functions():
        return [process_test]

    test_context = generate_context(0, 0, 0, 0)
    test_token = Token(TokenType.EOL, "", test_context)

    parser = BaseParser([test_token], Environment())
    parser._process_functions = process_functions

    with pytest.raises(MauException) as exc:
        parser.parse()

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == """Loop detected, cannot parse token: Token(TokenType.EOL, "", test.py:0,0-0,0)."""
    )
    process_test.assert_called()
