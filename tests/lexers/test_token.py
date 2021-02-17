from mau.lexers.base_lexer import Token


def test_token_accepts_type_and_value():
    t = Token("sometype", "somevalue")

    assert t.type == "sometype"
    assert t.value == "somevalue"


def test_token_transforms_value_in_string():
    t = Token("sometype", 3)

    assert t.type == "sometype"
    assert t.value == "3"


def test_token_keeps_value_none():
    t = Token("sometype", None)

    assert t.type == "sometype"
    assert t.value is None


def test_token_transforms_zero():
    t = Token("sometype", 0)

    assert t.type == "sometype"
    assert t.value == "0"


def test_token_value_defaults_to_none():
    t = Token("sometype")

    assert t.type == "sometype"
    assert t.value is None


def test_token_string_representation():
    t = Token("sometype", "somevalue")

    assert str(t) == "Token(sometype, 'somevalue')"


def test_token_representation():
    t = Token("sometype", "somevalue")

    assert repr(t) == "Token(sometype, 'somevalue')"


def test_token_equality():
    assert Token("sometype", "somevalue") == Token("sometype", "somevalue")


def test_token_length():
    t = Token("sometype", "somevalue")

    assert len(t) == len("somevalue")
    assert bool(t) is True


def test_empty_token_has_length_zero():
    t = Token("sometype")

    assert len(t) == 0
    assert bool(t) is True


def test_token_accepts_text_position():
    line = 456
    column = 123
    t = Token("sometype", "somevalue", position=(line, column))

    assert t.type == "sometype"
    assert t.value == "somevalue"
    assert t.position == (line, column)


def test_token_equality_ignores_position():
    assert Token("sometype", "somevalue", position=(12, 34)) == Token(
        "sometype", "somevalue"
    )
    assert Token("sometype", "somevalue") == Token(
        "sometype", "somevalue", position=(12, 34)
    )


def test_token_equality_accepts_none():
    assert Token("sometype", "somevalue") is not None


def test_token_string_representation_with_position():
    t = Token("sometype", "somevalue", position=(12, 34))

    assert str(t) == "Token(sometype, 'somevalue', line=12, col=34)"


def test_token_equality_with_any():
    assert Token("sometype", "somevalue") == Token("sometype")
