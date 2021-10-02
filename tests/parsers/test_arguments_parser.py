import pytest

from mau.parsers.base_parser import ParseError
from mau.parsers.arguments_parser import ArgumentsParser

from tests.helpers import init_parser_factory

init_parser = init_parser_factory(ArgumentsParser)


def test_named_argument():
    p = init_parser("argument1=value1")
    p.parse()

    assert p.args == []
    assert p.kwargs == {"argument1": "value1"}


def test_multiple_named_arguments():
    p = init_parser("argument1=value1,argument2=value2")
    p.parse()

    assert p.args == []
    assert p.kwargs == {"argument1": "value1", "argument2": "value2"}


def test_multiple_named_arguments_with_spaces():
    p = init_parser("argument1=value1, argument2=value2")
    p.parse()

    assert p.args == []
    assert p.kwargs == {"argument1": "value1", "argument2": "value2"}


def test_multiple_unnamed_arguments():
    p = init_parser("value1,value2")
    p.parse()

    assert p.args == ["value1", "value2"]
    assert p.kwargs == {}


def test_quotes_with_named_arguments():
    p = init_parser('argument="value1,value2"')
    p.parse()

    assert p.args == []
    assert p.kwargs == {"argument": "value1,value2"}


def test_quotes_with_unnamed_arguments():
    p = init_parser('"value1,value2"')
    p.parse()

    assert p.args == ["value1,value2"]
    assert p.kwargs == {}


def test_escaped_quotes():
    p = init_parser(r'"value \"with quotes\""')
    p.parse()

    assert p.args == ['value "with quotes"']
    assert p.kwargs == {}


def test_multiple_unnamed_and_named_arguments():
    p = init_parser("value1,argument2=value2")
    p.parse()

    assert p.args == ["value1"]
    assert p.kwargs == {"argument2": "value2"}


def test_multiple_named_arguments_before_unnamed_ones():
    p = init_parser("argument1=value1,value2")

    with pytest.raises(ParseError):
        p.parse()


def test_pop():
    p = init_parser("value1,value2")
    p.parse()

    assert p.pop() == "value1"
    assert p.args == ["value2"]
    assert p.kwargs == {}


def test_get_argumentss_and_reset():
    p = init_parser("value1,argument2=value2")
    p.parse()

    args, kwargs = p.get_arguments_and_reset()

    assert args == ["value1"]
    assert kwargs == {"argument2": "value2"}
    assert p.args == []
    assert p.kwargs == {}

    # This is internal but is important for the logic
    assert p._named_arguments is False
