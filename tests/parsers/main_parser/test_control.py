import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.content import ContentNode
from mau.nodes.header import HeaderNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.parsers.main_parser import MainParser
from mau.text_buffer.context import Context

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_initial_control():
    source = """
    """

    parser = runner(source)

    assert parser.control == (None, None, None)


def test_push_control():
    source = """
    """

    parser = runner(source)

    parser._push_control(
        "operator",
        "statement",
        Context(42, 128, "main", "@operator:statement"),
    )

    assert parser.control == (
        "operator",
        "statement",
        Context(42, 128, "main", "@operator:statement"),
    )


def test_pop_control_default():
    source = """
    """

    parser = runner(source)

    assert parser._pop_control() is True


def test_pop_control_equal():
    source = """
    :flag:42
    """

    parser = runner(source)

    parser._push_control("if", "flag:=42", Context(42, 128, "main", "@if:flag"))

    assert parser._pop_control() is True


def test_pop_control_not_equal():
    source = """
    :flag:42
    """

    parser = runner(source)

    parser._push_control("if", "flag:!=42", Context(42, 128, "main", "@if:flag"))

    assert parser._pop_control() is False


def test_pop_control_boolean_true():
    source = """
    :+flag:
    """

    parser = runner(source)

    parser._push_control("if", "flag:&true", Context(42, 128, "main", "@if:flag"))

    assert parser._pop_control() is True


def test_pop_control_boolean_false():
    source = """
    :+flag:
    """

    parser = runner(source)

    parser._push_control("if", "flag:&false", Context(42, 128, "main", "@if:flag"))

    assert parser._pop_control() is False


def test_pop_control_boolean_invalid():
    source = """
    :+flag:
    """

    parser = runner(source)

    parser._push_control("if", "flag:&something", Context(42, 128, "main", "@if:flag"))

    with pytest.raises(MauErrorException):
        parser._pop_control()


def test_pop_control_not_if():
    source = """
    """

    parser = runner(source)

    parser._push_control(
        "something", "flag:&something", Context(42, 128, "main", "@if:flag")
    )

    with pytest.raises(MauErrorException):
        parser._pop_control()


def test_pop_control_invalid_statement_format():
    source = """
    """

    parser = runner(source)

    parser._push_control("if", "flag=42", Context(42, 128, "main", "@if:flag"))

    with pytest.raises(MauErrorException):
        parser._pop_control()


def test_pop_control_variable_not_defined():
    source = """
    """

    parser = runner(source)

    parser._push_control("if", "flag:=42", Context(42, 128, "main", "@if:flag"))

    with pytest.raises(MauErrorException):
        parser._pop_control()


def test_pop_control_test_not_supported():
    source = """
    :+flag:
    """

    parser = runner(source)

    parser._push_control("if", "flag:*42", Context(42, 128, "main", "@if:flag"))

    with pytest.raises(MauErrorException):
        parser._pop_control()


def test_parse_control():
    source = """
    @operator:variable:test
    """

    parser = runner(source)

    assert parser.control == (
        "operator",
        "variable:test",
        Context(1, 0, "main", "@operator:variable:test"),
    )


def test_block_uses_control_true():
    source = """
    :+flag:
    
    @if:flag:&true
    ----
    ----
    """

    parser = runner(source)

    assert parser.nodes == [
        BlockNode(
            subtype=None,
            classes=[],
            title=None,
            engine=None,
            preprocessor="none",
            args=[],
            kwargs={},
        )
    ]

    assert parser.control == (None, None, None)


def test_block_uses_control_false():
    source = """
    :-flag:
    
    @if:flag:&true
    ----
    ----
    """

    parser = runner(source)

    assert parser.nodes == []

    assert parser.control == (None, None, None)


def test_include_content_uses_control_true():
    source = """
    :+flag:
    
    @if:flag:&true
    << ctype:/path/to/it
    """

    parser = runner(source)

    assert parser.nodes == [
        ContentNode(
            content_type="ctype",
            uris=["/path/to/it"],
            title=None,
        )
    ]

    assert parser.control == (None, None, None)


def test_include_content_uses_control_false():
    source = """
    :-flag:
    
    @if:flag:&true
    << ctype:/path/to/it
    """

    parser = runner(source)

    assert parser.nodes == []

    assert parser.control == (None, None, None)


def test_header_uses_control_true():
    environment = Environment()
    environment.setvar(
        "mau.parser.header_anchor_function", lambda text, level: "XXXXXX"
    )

    source = """
    :+flag:
    
    @if:flag:&true
    = Header
    """

    parser = runner(source, environment)

    assert parser.nodes == [
        HeaderNode(
            value=SentenceNode(children=[TextNode("Header")]),
            level="1",
            anchor="XXXXXX",
        )
    ]

    assert parser.control == (None, None, None)


def test_header_uses_control_false():
    source = """
    :-flag:
    
    @if:flag:&true
    = Header
    """

    parser = runner(source)

    assert parser.nodes == []

    assert parser.control == (None, None, None)


def test_paragraph_uses_control_true():
    source = """
    :+flag:
    
    @if:flag:&true
    This is a paragraph.
    """

    parser = runner(source)

    assert parser.nodes == [ParagraphNode(children=[TextNode("This is a paragraph.")])]

    assert parser.control == (None, None, None)


def test_paragraph_uses_control_false():
    source = """
    :-flag:
    
    @if:flag:&true
    This is a paragraph.
    """

    parser = runner(source)

    assert parser.nodes == []

    assert parser.control == (None, None, None)
