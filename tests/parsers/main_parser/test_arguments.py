import pytest
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_arguments_empty():
    source = """
    []
    """

    assert runner(source).attributes_manager.attributes == ([], {}, [], None)


def test_arguments_subtype():
    source = """
    [*subtype]
    """

    assert runner(source).attributes_manager.attributes == ([], {}, [], "subtype")


def test_arguments_multiple_subtypes():
    source = """
    [*subtype1, *subtype2]
    """

    with pytest.raises(MauErrorException):
        assert runner(source).attributes_manager.attributes == ([], {}, [], "subtype1")


def test_arguments_args():
    source = """
    [arg1,arg2]
    """

    assert runner(source).attributes_manager.attributes == (
        ["arg1", "arg2"],
        {},
        [],
        None,
    )


def test_arguments_kwargs():
    source = """
    [key1=value1,key2=value2]
    """

    assert runner(source).attributes_manager.attributes == (
        [],
        {"key1": "value1", "key2": "value2"},
        [],
        None,
    )


def test_arguments_support_variables():
    source = """
    :arg1:number1
    :value1:42

    [{arg1},key1={value1}]
    """

    assert runner(source).attributes_manager.attributes == (
        ["number1"],
        {"key1": "42"},
        [],
        None,
    )


def test_arguments_tags():
    source = """
    [#tag1,#tag2]
    """

    assert runner(source).attributes_manager.attributes == (
        [],
        {},
        ["tag1", "tag2"],
        None,
    )
