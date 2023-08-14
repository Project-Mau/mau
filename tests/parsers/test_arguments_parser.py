import pytest
from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.nodes.arguments import NamedArgumentNode, UnnamedArgumentNode
from mau.parsers.arguments import set_names_and_defaults
from mau.parsers.arguments_parser import ArgumentsParser
from mau.parsers.base_parser import ParserError

from tests.helpers import parser_runner_factory

runner = parser_runner_factory(ArgumentsLexer, ArgumentsParser)


def test_single_unnamed_argument_no_spaces():
    source = "value1"

    assert runner(source).nodes == [UnnamedArgumentNode("value1")]


def test_single_unnamed_argument_with_spaces():
    source = "value with spaces"

    assert runner(source).nodes == [UnnamedArgumentNode("value with spaces")]


def test_multiple_unnamed_arguments_no_spaces():
    source = "value1,value2"

    assert runner(source).nodes == [
        UnnamedArgumentNode("value1"),
        UnnamedArgumentNode("value2"),
    ]


def test_multiple_unnamed_arguments_with_spaces():
    source = "value1 with spaces,value2 with more spaces"

    assert runner(source).nodes == [
        UnnamedArgumentNode("value1 with spaces"),
        UnnamedArgumentNode("value2 with more spaces"),
    ]


def test_multiple_unnamed_arguments_space_after_comma_is_removed():
    source = "value1 with spaces, value2 with more spaces"

    assert runner(source).nodes == [
        UnnamedArgumentNode("value1 with spaces"),
        UnnamedArgumentNode("value2 with more spaces"),
    ]


def test_multiple_unnamed_arguments_multiple_spaces_after_comma_is_removed():
    source = "value1 with spaces,    value2 with more spaces"

    assert runner(source).nodes == [
        UnnamedArgumentNode("value1 with spaces"),
        UnnamedArgumentNode("value2 with more spaces"),
    ]


def test_single_unnamed_argument_with_quotes_no_spaces():
    source = '"value1"'

    assert runner(source).nodes == [UnnamedArgumentNode("value1")]


def test_single_unnamed_argument_with_quotes_with_spaces():
    source = '"value with spaces"'

    assert runner(source).nodes == [UnnamedArgumentNode("value with spaces")]


def test_single_unnamed_argument_comma_is_ignored_between_quotes():
    source = '"value1,value2"'

    assert runner(source).nodes == [UnnamedArgumentNode("value1,value2")]


def test_multiple_unnamed_arguments_with_quotes_no_spaces():
    source = '"value1","value2"'

    assert runner(source).nodes == [
        UnnamedArgumentNode("value1"),
        UnnamedArgumentNode("value2"),
    ]


def test_multiple_unnamed_arguments_with_quotes_with_spaces():
    source = '"value1 with spaces","value2 with more spaces"'

    assert runner(source).nodes == [
        UnnamedArgumentNode("value1 with spaces"),
        UnnamedArgumentNode("value2 with more spaces"),
    ]


def test_single_unnamed_argument_with_non_delimiting_quotes():
    source = r'value "with quotes"'

    assert runner(source).nodes == [UnnamedArgumentNode('value "with quotes"')]


def test_single_unnamed_argument_with_escaped_quotes():
    source = r'"value \"with escaped quotes\""'

    assert runner(source).nodes == [UnnamedArgumentNode('value "with escaped quotes"')]


def test_single_named_argument():
    source = "name=value1"

    assert runner(source).nodes == [
        NamedArgumentNode("name", "value1"),
    ]


def test_single_named_argument_with_spaces():
    source = "name=value with spaces"

    assert runner(source).nodes == [
        NamedArgumentNode("name", "value with spaces"),
    ]


def test_multiple_named_arguments():
    source = "name1=value1,name2=value2"

    assert runner(source).nodes == [
        NamedArgumentNode("name1", "value1"),
        NamedArgumentNode("name2", "value2"),
    ]


def test_multiple_named_arguments_with_spaces():
    source = "name1=value1 with spaces,name2=value2 with spaces"

    assert runner(source).nodes == [
        NamedArgumentNode("name1", "value1 with spaces"),
        NamedArgumentNode("name2", "value2 with spaces"),
    ]


def test_multiple_named_arguments_space_after_comma_is_removed():
    source = "name1=value1, name2=value2"

    assert runner(source).nodes == [
        NamedArgumentNode("name1", "value1"),
        NamedArgumentNode("name2", "value2"),
    ]


def test_multiple_named_arguments_multiple_spaces_after_comma_is_removed():
    source = "name1=value1,    name2=value2"

    assert runner(source).nodes == [
        NamedArgumentNode("name1", "value1"),
        NamedArgumentNode("name2", "value2"),
    ]


def test_single_named_argument_with_quotes_no_spaces():
    source = 'name="value1"'

    assert runner(source).nodes == [NamedArgumentNode("name", "value1")]


def test_single_named_argument_with_quotes_with_spaces():
    source = 'name="value with spaces"'

    assert runner(source).nodes == [NamedArgumentNode("name", "value with spaces")]


def test_single_named_argument_comma_is_ignored_between_quotes():
    source = 'name="value1,value2"'

    assert runner(source).nodes == [NamedArgumentNode("name", "value1,value2")]


def test_multiple_named_arguments_with_quotes_no_spaces():
    source = 'name1="value1",name2="value2"'

    assert runner(source).nodes == [
        NamedArgumentNode("name1", "value1"),
        NamedArgumentNode("name2", "value2"),
    ]


def test_multiple_named_arguments_with_quotes_with_spaces():
    source = 'name1="value1 with spaces",name2="value2 with more spaces"'

    assert runner(source).nodes == [
        NamedArgumentNode("name1", "value1 with spaces"),
        NamedArgumentNode("name2", "value2 with more spaces"),
    ]


def test_single_named_argument_with_non_delimiting_quotes():
    source = r'name=value "with quotes"'

    assert runner(source).nodes == [NamedArgumentNode("name", 'value "with quotes"')]


def test_single_named_argument_with_escaped_quotes():
    source = r'name="value \"with escaped quotes\""'

    assert runner(source).nodes == [
        NamedArgumentNode("name", 'value "with escaped quotes"')
    ]


def test_unnamed_and_named_arguments():
    source = "value1, name=value2"

    assert runner(source).nodes == [
        UnnamedArgumentNode("value1"),
        NamedArgumentNode("name", "value2"),
    ]


def test_named_arguments_followed_by_unnamed():
    source = "name=value2, value1"

    with pytest.raises(ParserError):
        runner(source)


def test_apply_prototype_unnamed_arguments():
    args, kwargs = set_names_and_defaults(
        args=["value1", "value2"],
        kwargs={},
        positional_names=["attr1", "attr2"],
        default_values={"attr3": "value3"},
    )

    assert args == []
    assert kwargs == {"attr1": "value1", "attr2": "value2", "attr3": "value3"}


def test_apply_prototype_unnamed_and_named_arguments():
    parser = ArgumentsParser(tokens=[])

    parser.nodes = [
        UnnamedArgumentNode("value1"),
        UnnamedArgumentNode("value2"),
        NamedArgumentNode("attr5", "value5"),
    ]

    args, kwargs, tags = parser.process_arguments()

    args, kwargs = set_names_and_defaults(
        args, kwargs, ["attr1", "attr2"], {"attr3": "value3"}
    )

    assert args == []
    assert kwargs == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value3",
        "attr5": "value5",
    }
    assert tags == []


def test_apply_prototype_clash_between_default_value_and_named_value():
    parser = ArgumentsParser(tokens=[])

    parser.nodes = [
        UnnamedArgumentNode("value1"),
        UnnamedArgumentNode("value2"),
        NamedArgumentNode("attr3", "value5"),
    ]

    args, kwargs, tags = parser.process_arguments()

    args, kwargs = set_names_and_defaults(
        args, kwargs, ["attr1", "attr2"], {"attr3": "value3"}
    )

    assert args == []
    assert kwargs == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value5",
    }
    assert tags == []


def test_apply_prototype_clash_between_positional_value_and_named_value():
    parser = ArgumentsParser(tokens=[])

    parser.nodes = [
        UnnamedArgumentNode("value1"),
        UnnamedArgumentNode("value2"),
        NamedArgumentNode("attr1", "value5"),
    ]

    args, kwargs, tags = parser.process_arguments()

    args, kwargs = set_names_and_defaults(
        args, kwargs, ["attr1", "attr2"], {"attr3": "value3"}
    )

    assert args == []
    assert kwargs == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value3",
    }
    assert tags == []


def test_apply_prototype_clash_in_prototype():
    parser = ArgumentsParser(tokens=[])

    parser.nodes = [
        UnnamedArgumentNode("value1"),
        UnnamedArgumentNode("value2"),
        NamedArgumentNode("attr3", "value3"),
    ]

    args, kwargs, tags = parser.process_arguments()

    args, kwargs = set_names_and_defaults(
        args, kwargs, ["attr1", "attr2"], {"attr1": "value7"}
    )

    assert args == []
    assert kwargs == {
        "attr1": "value1",
        "attr2": "value2",
        "attr3": "value3",
    }
    assert tags == []


def test_apply_prototype_positional_values_not_provided():
    parser = ArgumentsParser(tokens=[])

    parser.nodes = [UnnamedArgumentNode("value1")]

    args, kwargs, _ = parser.process_arguments()

    with pytest.raises(ValueError):
        set_names_and_defaults(args, kwargs, ["attr1", "attr2"], {"attr3": "value3"})


def test_apply_prototype_positional_values_without_name():
    parser = ArgumentsParser(tokens=[])

    parser.nodes = [UnnamedArgumentNode("value1"), UnnamedArgumentNode("value2")]

    args, kwargs, tags = parser.process_arguments()

    args, kwargs = set_names_and_defaults(args, kwargs, ["attr1"], {"attr3": "value3"})

    assert args == ["value2"]
    assert kwargs == {
        "attr1": "value1",
        "attr3": "value3",
    }
    assert tags == []


def test_apply_prototype_missing_positional_with_default():
    parser = ArgumentsParser(tokens=[])

    parser.nodes = [
        NamedArgumentNode("attr1", "value5"),
    ]

    args, kwargs, tags = parser.process_arguments()

    args, kwargs = set_names_and_defaults(args, kwargs, ["attr1"])

    assert args == []
    assert kwargs == {
        "attr1": "value5",
    }
    assert tags == []
