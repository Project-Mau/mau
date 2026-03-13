import pytest

from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_variable_definition_without_value_is_empty():
    source = """
    :attr:
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Error in variable definition. Variable 'attr' has no value."
    )
    assert exc.value.message.context == generate_context(1, 0, 1, 6)


def test_variable_definition_with_plus_is_true():
    source = """
    :+attr:
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment["attr"] == "true"


def test_variable_definition_with_minus_is_false():
    source = """
    :-attr:
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment["attr"] == "false"


def test_variable_definition_flag_plus_ignores_value():
    source = """
    :+attr:42
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment["attr"] == "true"


def test_variable_definition_flag_minus_ignores_value():
    source = """
    :-attr:42
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment["attr"] == "false"


def test_variable_definition_with_value_is_loaded():
    source = """
    :attr:42
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment["attr"] == "42"


def test_variable_definition_multiple():
    source = """
    :attr1:42
    :attr2:43
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment["attr1"] == "42"
    assert parser.environment["attr2"] == "43"


def test_variable_definition_value_can_be_any_text():
    source = """
    :attr:[footnote](http://some.domain/path)
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment["attr"] == "[footnote](http://some.domain/path)"


def test_variable_definition_with_namespace():
    source = """
    :meta.attr:42
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.get("meta").asdict() == {"attr": "42"}


def test_variable_definition_with_multiple_dots():
    source = """
    :meta.category.attr:42
    """

    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.get("meta").asdict() == {"category": {"attr": "42"}}
