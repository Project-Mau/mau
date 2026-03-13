from mau.test_helpers import TEST_CONTEXT_SOURCE, compare_asdict_list, generate_context
from mau.text_buffer import Context
from mau.token import Token, TokenType


def test_token_accepts_type_and_value():
    token = Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4))

    assert token.type == TokenType.TEXT
    assert token.value == "somevalue"
    assert token.context == generate_context(1, 2, 3, 4)


def test_token_repr():
    token = Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4))

    assert (
        repr(token)
        == f"""Token(TokenType.TEXT, "somevalue", {TEST_CONTEXT_SOURCE}:1,2-3,4)"""
    )


def test_token_as_dict():
    token = Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4))

    assert token.asdict() == {
        "type": TokenType.TEXT,
        "value": "somevalue",
        "context": {
            "start_line": 1,
            "start_column": 2,
            "end_line": 3,
            "end_column": 4,
            "source": TEST_CONTEXT_SOURCE,
        },
    }


def test_token_equality():
    assert (
        Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4)) != "somevalue"
    )
    assert Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4)) == Token(
        TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4)
    )


def test_token_equality_considers_value():
    assert Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4)) != Token(
        TokenType.TEXT, "othervalue", generate_context(1, 2, 3, 4)
    )


def test_token_equality_considers_type():
    assert Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4)) != Token(
        TokenType.LABEL, "somevalue", generate_context(1, 2, 3, 4)
    )


def test_token_equality_ignores_context():
    assert Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4)) == Token(
        TokenType.TEXT, "somevalue", generate_context(2, 3, 4, 5)
    )


def test_token_length():
    token = Token(TokenType.TEXT, "somevalue", generate_context(1, 2, 3, 4))

    assert len(token) == len("somevalue")


def test_empty_token_has_length_zero():
    token = Token(TokenType.TEXT, "", generate_context(1, 2, 3, 4))

    assert len(token) == 0


def test_token_from_list():
    tokens = [
        Token(TokenType.TEXT, "This is ", generate_context(0, 0, 0, 8)),
        Token(TokenType.TEXT, "a list ", generate_context(0, 8, 0, 15)),
        Token(TokenType.TEXT, "of tokens.", generate_context(0, 15, 0, 25)),
    ]

    token = Token.from_token_list(tokens)

    assert token.type == TokenType.TEXT
    assert token.value == "This is a list of tokens."
    assert token.context == generate_context(0, 0, 0, 25)


def test_token_from_empty_list():
    token = Token.from_token_list([])

    assert token.type == TokenType.TEXT
    assert token.value == ""
    assert token.context == Context(0, 0, 0, 0)


def test_token_to_list():
    token = Token(
        TokenType.TEXT, "This is \na list \nof tokens.", generate_context(0, 0, 2, 25)
    )

    tokens = token.to_token_list()

    compare_asdict_list(
        tokens,
        [
            Token(TokenType.TEXT, "This is ", generate_context(0, 0, 0, 8)),
            Token(TokenType.TEXT, "a list ", generate_context(1, 0, 1, 7)),
            Token(TokenType.TEXT, "of tokens.", generate_context(2, 0, 2, 10)),
        ],
    )


def test_token_to_list_single_line():
    token = Token(
        TokenType.TEXT, "This is a single token.", generate_context(0, 0, 0, 23)
    )

    tokens = token.to_token_list()

    compare_asdict_list(
        tokens,
        [
            Token(
                TokenType.TEXT, "This is a single token.", generate_context(0, 0, 0, 23)
            ),
        ],
    )


def test_token_to_list_empty():
    token = Token(TokenType.TEXT, "", generate_context(0, 0, 0, 0))

    tokens = token.to_token_list()

    compare_asdict_list(
        tokens,
        [
            Token(TokenType.TEXT, "", generate_context(0, 0, 0, 0)),
        ],
    )
