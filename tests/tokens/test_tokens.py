from mau.tokens.tokens import Context, Token


def test_token_accepts_type_and_value():
    token = Token("sometype", "somevalue")

    assert token.type == "sometype"
    assert token.value == "somevalue"
    assert token != "somevalue"


def test_token_keeps_value_none():
    token = Token("sometype", None)

    assert token.type == "sometype"
    assert token.value == ""


def test_token_value_defaults_to_none():
    token = Token("sometype")

    assert token.type == "sometype"
    assert token.value == ""


def test_token_equality():
    assert Token("sometype", "somevalue") == Token("sometype", "somevalue")


def test_token_length():
    token = Token("sometype", "somevalue")

    assert len(token) == len("somevalue")
    assert bool(token) is True


def test_empty_token_has_length_zero():
    token = Token("sometype")

    assert len(token) == 0
    assert bool(token) is True


def test_token_accepts_context():
    context = Context(source="main", text="sometext", line=123, column=456)

    token = Token("sometype", "somevalue", context=context)

    assert token.type == "sometype"
    assert token.value == "somevalue"
    assert token.context == context


def test_token_equality_ignores_context():
    context = Context(source="main", text="sometext", line=123, column=456)

    assert Token("sometype", "somevalue", context=context) == Token(
        "sometype", "somevalue"
    )
    assert Token("sometype", "somevalue") == Token(
        "sometype", "somevalue", context=context
    )


def test_token_equality_accepts_none():
    assert Token("sometype", "somevalue") is not None


def test_token_equality_with_any():
    assert Token("sometype", "somevalue") == Token("sometype")


def test_token_match_considers_context():
    context = Context(source="main", text="sometext", line=123, column=456)

    assert not Token("sometype", "somevalue", context=context).match(
        Token("sometype", "somevalue")
    )
    assert not Token("sometype", "somevalue").match(
        Token("sometype", "somevalue", context=context)
    )
    assert Token("sometype", "somevalue", context=context).match(
        Token("sometype", "somevalue", context=context)
    )
