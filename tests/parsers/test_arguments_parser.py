import pytest

from mau.parsers.base_parser import ParserError
from mau.parsers.arguments_parser import ArgumentsParser

from tests.helpers import init_parser_factory

init_parser = init_parser_factory(ArgumentsParser)


def test_single_unnamed_argument_no_spaces():
    p = init_parser("value")
    p.parse()

    assert p.args == ["value"]
    assert p.kwargs == {}


def test_single_unnamed_argument_with_spaces():
    p = init_parser("value with spaces")
    p.parse()

    assert p.args == ["value with spaces"]
    assert p.kwargs == {}


def test_multiple_unnamed_arguments_no_spaces():
    p = init_parser("value1,value2")
    p.parse()

    assert p.args == ["value1", "value2"]
    assert p.kwargs == {}


def test_multiple_unnamed_arguments_with_spaces():
    p = init_parser("value1 with spaces,value2 with other spaces")
    p.parse()

    assert p.args == ["value1 with spaces", "value2 with other spaces"]
    assert p.kwargs == {}


def test_multiple_unnamed_arguments_space_after_comma_is_removed():
    p = init_parser("value1 with spaces, value2 with other spaces")
    p.parse()

    assert p.args == ["value1 with spaces", "value2 with other spaces"]
    assert p.kwargs == {}


def test_single_unnamed_argument_with_quotes_no_spaces():
    p = init_parser('"value"')
    p.parse()

    assert p.args == ["value"]
    assert p.kwargs == {}


def test_single_unnamed_argument_with_quotes_with_spaces():
    p = init_parser('"value with spaces"')
    p.parse()

    assert p.args == ["value with spaces"]
    assert p.kwargs == {}


def test_single_unnamed_argument_comma_is_ignored_between_quotes():
    p = init_parser('"value1,value2"')
    p.parse()

    assert p.args == ["value1,value2"]
    assert p.kwargs == {}


def test_multiple_unnamed_arguments_with_quotes_no_spaces():
    p = init_parser('"value1","value2"')
    p.parse()

    assert p.args == ["value1", "value2"]
    assert p.kwargs == {}


def test_multiple_unnamed_arguments_with_quotes_with_spaces():
    p = init_parser('"value1 with spaces","value2 with other spaces"')
    p.parse()

    assert p.args == ["value1 with spaces", "value2 with other spaces"]
    assert p.kwargs == {}


def test_single_unnamed_argument_with_non_delimiting_quotes():
    p = init_parser(r'value "with quotes"')
    p.parse()

    assert p.args == ['value "with quotes"']
    assert p.kwargs == {}


def test_single_unnamed_argument_with_escaped_quotes():
    p = init_parser(r'"value \"with escaped quotes\""')
    p.parse()

    assert p.args == ['value "with escaped quotes"']
    assert p.kwargs == {}


def test_single_named_argument():
    p = init_parser("name=value")
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name": "value"}


def test_single_named_argument_with_spaces():
    p = init_parser("name=value with spaces")
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name": "value with spaces"}


def test_multiple_named_arguments():
    p = init_parser("name1=value1,name2=value2")
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name1": "value1", "name2": "value2"}


def test_multiple_named_arguments_with_spaces():
    p = init_parser("name1=value1 with spaces,name2=value2 with spaces")
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name1": "value1 with spaces", "name2": "value2 with spaces"}


def test_multiple_named_arguments_space_after_comma_is_removed():
    p = init_parser("name1=value1, name2=value2")
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name1": "value1", "name2": "value2"}


def test_single_named_argument_with_quotes_no_spaces():
    p = init_parser('name="value"')
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name": "value"}


def test_single_named_argument_with_quotes_with_spaces():
    p = init_parser('name="value with spaces"')
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name": "value with spaces"}


def test_single_named_argument_comma_is_ignored_between_quotes():
    p = init_parser('name="value1,value2"')
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name": "value1,value2"}


def test_multiple_named_arguments_with_quotes_no_spaces():
    p = init_parser('name1="value1",name2="value2"')
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name1": "value1", "name2": "value2"}


def test_multiple_named_arguments_with_quotes_with_spaces():
    p = init_parser('name1="value1 with spaces",name2="value2 with other spaces"')
    p.parse()

    assert p.args == []
    assert p.kwargs == {
        "name1": "value1 with spaces",
        "name2": "value2 with other spaces",
    }


def test_single_named_argument_with_non_delimiting_quotes():
    p = init_parser(r'name=value "with quotes"')
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name": 'value "with quotes"'}


def test_single_named_argument_with_escaped_quotes():
    p = init_parser(r'name="value \"with escaped quotes\""')
    p.parse()

    assert p.args == []
    assert p.kwargs == {"name": 'value "with escaped quotes"'}


def test_apply_prototype_unnamed_arguments():
    p = init_parser("value1, value2")
    p.parse()
    p.set_names_and_defaults(["attr1", "attr2"], {"attr3": "value3"})

    assert p.args == []
    assert p.kwargs == {"attr1": "value1", "attr2": "value2", "attr3": "value3"}


def test_apply_prototype_unnamed_and_named_arguments():
    p = init_parser("value1, value2, attr5=value5")
    p.parse()
    p.set_names_and_defaults(["attr1", "attr2"], {"attr3": "value3"})

    assert p.args == []
    assert p.kwargs == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value3",
        "attr5": "value5",
    }


def test_apply_prototype_clash_between_default_and_named():
    p = init_parser("value1, value2, attr3=value5")
    p.parse()
    p.set_names_and_defaults(["attr1", "attr2"], {"attr3": "value3"})

    assert p.args == []
    assert p.kwargs == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value5",
    }


def test_apply_prototype_clash_between_positional_and_named():
    p = init_parser("value1, value2, attr1=value5")
    p.parse()
    p.set_names_and_defaults(["attr1", "attr2"], {"attr3": "value3"})

    assert p.args == []
    assert p.kwargs == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value3",
    }


def test_apply_prototype_clash_in_prototype():
    p = init_parser("value1, value2, attr3=value3")
    p.parse()
    p.set_names_and_defaults(["attr1", "attr2"], {"attr1": "value7"})

    assert p.args == []
    assert p.kwargs == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value3",
    }


def test_apply_prototype_positional_values_not_provided():
    p = init_parser("value1")
    p.parse()

    with pytest.raises(ParserError):
        p.set_names_and_defaults(["attr1", "attr2"], {"attr3": "value3"})


def test_apply_prototype_too_many_positional_values():
    p = init_parser("value1, value2")
    p.parse()

    with pytest.raises(ParserError):
        p.set_names_and_defaults(["attr1"], {"attr3": "value3"})


def test_apply_prototype_missing_positional_with_default():
    p = init_parser("attr1=value5")
    p.parse()
    p.set_names_and_defaults(["attr1"], {})

    assert p.args == []
    assert p.kwargs == {
        "attr1": "value5",
    }
