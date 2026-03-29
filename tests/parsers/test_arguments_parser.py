from unittest.mock import patch

import pytest

from mau.environment.environment import Environment
from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.message import MauException, MauMessageType
from mau.nodes.node import NodeInfo, ValueNode
from mau.nodes.node_arguments import NodeArguments
from mau.parsers.arguments_parser import ArgumentsParser, set_names
from mau.test_helpers import (
    compare_nodes,
    compare_nodes_map,
    compare_nodes_sequence,
    generate_context,
    parser_runner_factory,
)

runner = parser_runner_factory(ArgumentsLexer, ArgumentsParser)


def test_single_unnamed_argument_no_spaces():
    source = "value1"

    expected = [
        ValueNode(
            "value1",
            info=NodeInfo(
                context=generate_context(0, 0, 0, 6),
            ),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_unnamed_argument_with_spaces():
    source = "value with spaces"

    expected = [
        ValueNode(
            "value with spaces",
            info=NodeInfo(context=generate_context(0, 0, 0, 17)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_unnamed_arguments_no_spaces():
    source = "value1,value2"

    expected = [
        ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 0, 0, 6)),
        ),
        ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 7, 0, 13)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_unnamed_arguments_with_spaces():
    source = "value1 with spaces,value2 with more spaces"

    expected = [
        ValueNode(
            "value1 with spaces",
            info=NodeInfo(context=generate_context(0, 0, 0, 18)),
        ),
        ValueNode(
            "value2 with more spaces",
            info=NodeInfo(context=generate_context(0, 19, 0, 42)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_unnamed_arguments_space_after_comma_is_removed():
    source = "value1 with spaces, value2 with more spaces"

    expected = [
        ValueNode(
            "value1 with spaces",
            info=NodeInfo(context=generate_context(0, 0, 0, 18)),
        ),
        ValueNode(
            "value2 with more spaces",
            info=NodeInfo(context=generate_context(0, 20, 0, 43)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_unnamed_arguments_multiple_spaces_after_comma_is_removed():
    source = "value1 with spaces,    value2 with more spaces"

    expected = [
        ValueNode(
            "value1 with spaces",
            info=NodeInfo(context=generate_context(0, 0, 0, 18)),
        ),
        ValueNode(
            "value2 with more spaces",
            info=NodeInfo(context=generate_context(0, 23, 0, 46)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_unnamed_argument_with_quotes_no_spaces():
    source = '"value1"'

    expected = [
        ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 1, 0, 7)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_unnamed_argument_with_quotes_with_spaces():
    source = '"value with spaces"'

    expected = [
        ValueNode(
            "value with spaces",
            info=NodeInfo(context=generate_context(0, 1, 0, 18)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_unnamed_argument_comma_is_ignored_between_quotes():
    source = '"value1,value2"'

    expected = [
        ValueNode(
            "value1,value2",
            info=NodeInfo(context=generate_context(0, 1, 0, 14)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_unnamed_arguments_with_quotes_no_spaces():
    source = '"value1","value2"'

    expected = [
        ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 1, 0, 7)),
        ),
        ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 10, 0, 16)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_unnamed_arguments_with_quotes_with_spaces():
    source = '"value1 with spaces","value2 with more spaces"'

    expected = [
        ValueNode(
            "value1 with spaces",
            info=NodeInfo(context=generate_context(0, 1, 0, 19)),
        ),
        ValueNode(
            "value2 with more spaces",
            info=NodeInfo(context=generate_context(0, 22, 0, 45)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_unnamed_argument_with_non_delimiting_quotes():
    source = r'value "with quotes"'

    expected = [
        ValueNode(
            'value "with quotes"',
            info=NodeInfo(context=generate_context(0, 0, 0, 19)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_unnamed_argument_with_escaped_quotes():
    source = r'"value \"with escaped quotes\""'

    expected = [
        ValueNode(
            'value "with escaped quotes"',
            info=NodeInfo(context=generate_context(0, 1, 0, 30)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_named_argument():
    source = "name=value1"

    expected = {
        "name": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 5, 0, 11)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_named_argument_with_spaces():
    source = "name=value with spaces"

    expected = {
        "name": ValueNode(
            "value with spaces",
            info=NodeInfo(context=generate_context(0, 5, 0, 22)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_named_arguments():
    source = "name1=value1,name2=value2"

    expected = {
        "name1": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 6, 0, 12)),
        ),
        "name2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 19, 0, 25)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_named_arguments_with_spaces():
    source = "name1=value1 with spaces,name2=value2 with spaces"

    expected = {
        "name1": ValueNode(
            "value1 with spaces",
            info=NodeInfo(context=generate_context(0, 6, 0, 24)),
        ),
        "name2": ValueNode(
            "value2 with spaces",
            info=NodeInfo(context=generate_context(0, 31, 0, 49)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_named_arguments_space_after_comma_is_removed():
    source = "name1=value1, name2=value2"

    expected = {
        "name1": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 6, 0, 12)),
        ),
        "name2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 20, 0, 26)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_named_arguments_multiple_spaces_after_comma_is_removed():
    source = "name1=value1,    name2=value2"

    expected = {
        "name1": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 6, 0, 12)),
        ),
        "name2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 23, 0, 29)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_named_argument_with_quotes_no_spaces():
    source = 'name="value1"'

    expected = {
        "name": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 6, 0, 12)),
        )
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_named_argument_with_quotes_with_spaces():
    source = 'name="value with spaces"'

    expected = {
        "name": ValueNode(
            "value with spaces",
            info=NodeInfo(context=generate_context(0, 6, 0, 23)),
        )
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_named_argument_comma_is_ignored_between_quotes():
    source = 'name="value1,value2"'

    expected = {
        "name": ValueNode(
            "value1,value2",
            info=NodeInfo(context=generate_context(0, 6, 0, 19)),
        )
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_named_arguments_with_quotes_no_spaces():
    source = 'name1="value1",name2="value2"'

    expected = {
        "name1": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 7, 0, 13)),
        ),
        "name2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 22, 0, 28)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_multiple_named_arguments_with_quotes_with_spaces():
    source = 'name1="value1 with spaces",name2="value2 with more spaces"'

    expected = {
        "name1": ValueNode(
            "value1 with spaces",
            info=NodeInfo(context=generate_context(0, 7, 0, 25)),
        ),
        "name2": ValueNode(
            "value2 with more spaces",
            info=NodeInfo(context=generate_context(0, 34, 0, 57)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_named_argument_with_non_delimiting_quotes():
    source = r'name=value "with quotes"'
    expected = {
        "name": ValueNode(
            'value "with quotes"',
            info=NodeInfo(context=generate_context(0, 5, 0, 24)),
        )
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_single_named_argument_with_escaped_quotes():
    source = r'name="value \"with escaped quotes\""'

    expected = {
        "name": ValueNode(
            'value "with escaped quotes"',
            info=NodeInfo(context=generate_context(0, 6, 0, 35)),
        )
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_unnamed_and_named_arguments():
    source = "value1, name=value2"

    expected_unnamed_nodes = [
        ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 0, 0, 6)),
        )
    ]

    expected_named_nodes = {
        "name": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 13, 0, 19)),
        ),
    }

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, expected_named_nodes)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_named_arguments_followed_by_unnamed():
    source = "name=value2, value1"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Unnamed arguments after named arguments are forbidden."
    )


def test_process_arguments_subtype():
    source = "value1, *subtype1"

    expected_unnamed_nodes = [
        ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 0, 0, 6)),
        ),
    ]

    expected_subtype = ValueNode(
        "subtype1",
        info=NodeInfo(context=generate_context(0, 8, 0, 17)),
    )

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    compare_nodes(parser.subtype, expected_subtype)


def test_process_arguments_tags():
    source = "value1, #tag1, value2, #tag2"

    expected_unnamed_nodes = [
        ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 0, 0, 6)),
        ),
        ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 15, 0, 21)),
        ),
    ]
    expected_tag_nodes = [
        ValueNode(
            "tag1",
            info=NodeInfo(context=generate_context(0, 8, 0, 13)),
        ),
        ValueNode(
            "tag2",
            info=NodeInfo(context=generate_context(0, 23, 0, 28)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, expected_tag_nodes)
    assert parser.subtype is None


def test_process_arguments_multiple_subtypes():
    source = "*value1, *value2"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Multiple nodes with prefix '*' detected."


def test_arguments():
    source = "value1, #tag1, #mau:tag2, *subtype1, name=value2"

    parser = runner(source)

    assert parser.arguments == NodeArguments(
        unnamed_args=["value1"],
        named_args={"name": "value2"},
        tags=["tag1"],
        internal_tags=["tag2"],
        subtype="subtype1",
    )


def test_process_arguments_alias_replacement():
    # Test that a given alias can be configured
    # to be used to add named arguments.
    # In this test,
    # "arg1, @alias1"
    # is replaced with
    # "arg1, @alias1, key1=value1, key2=value2"

    environment = Environment()
    environment["mau.parser.aliases"] = {
        "alias1": {
            "args": {"key1": "value1", "key2": "value2"},
            "names": [],
            "subtype": None,
        }
    }

    source = "arg1, @alias1"

    expected_unnamed_nodes = [
        ValueNode(
            "arg1",
            info=NodeInfo(context=generate_context(0, 0, 0, 4)),
        ),
    ]

    expected_named_nodes = {
        "key1": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 6, 0, 13)),
        ),
        "key2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 6, 0, 13)),
        ),
    }

    parser = runner(source, environment)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, expected_named_nodes)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_process_arguments_alias_replacement_names_and_subtype_default():
    # Test that replacement names and subtype
    # have a sensible default.

    environment = Environment()
    environment["mau.parser.aliases"] = {
        "alias1": {
            "args": {"key1": "value1", "key2": "value2"},
        }
    }

    source = "arg1, @alias1"

    expected_unnamed_nodes = [
        ValueNode(
            "arg1",
            info=NodeInfo(context=generate_context(0, 0, 0, 4)),
        ),
    ]

    expected_named_nodes = {
        "key1": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 6, 0, 13)),
        ),
        "key2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 6, 0, 13)),
        ),
    }

    parser = runner(source, environment)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, expected_named_nodes)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_process_arguments_empty_alias_replacement_leaves_arguments_untouched():
    # Test that replacement names and subtype
    # have a sensible default.

    environment = Environment()
    environment["mau.parser.aliases"] = {"alias1": {}}

    source = "arg1, @alias1"

    expected_unnamed_nodes = [
        ValueNode(
            "arg1",
            info=NodeInfo(context=generate_context(0, 0, 0, 4)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_process_arguments_alias_not_present():
    # Test that if the alias is not present
    # we receive an error.

    source = "arg1, @alias1"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Alias 'alias1' cannot be found in 'mau.parser.aliases': {}."
    )


def test_process_arguments_alias_replacement_does_not_overwrite_arguments():
    # Test that existing arguments are not replaced
    # when the alias is expanded.
    # In this test,
    # "arg1, @alias1, key1=originalvalue1"
    # is replaced with
    # "arg1, key1=originalvalue1, key2=value2"

    environment = Environment()
    environment["mau.parser.aliases"] = {
        "alias1": {"args": {"key1": "value1", "key2": "value2"}, "names": []}
    }

    source = "arg1, @alias1, key1=originalvalue1"

    expected_unnamed_nodes = [
        ValueNode(
            "arg1",
            info=NodeInfo(context=generate_context(0, 0, 0, 4)),
        ),
    ]

    expected_named_nodes = {
        "key1": ValueNode(
            "originalvalue1",
            info=NodeInfo(context=generate_context(0, 20, 0, 34)),
        ),
        "key2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 6, 0, 13)),
        ),
    }

    parser = runner(source, environment)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, expected_named_nodes)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_process_arguments_alias_replacement_supports_names():
    # Test that the replacement can provide names
    # for unnamed arguments, and that they are applied.
    # In this test,
    # "arg1, @alias1"
    # is replaced with
    # "somename=arg1, key1=value1, key2=value2"

    environment = Environment()
    environment["mau.parser.aliases"] = {
        "alias1": {
            "args": {"key1": "value1", "key2": "value2"},
            "names": ["somename"],
        }
    }

    # These are out of order to check
    # that names are applied to actual
    # unnamed arguments and not to
    # the first argument.
    source = "@alias1, arg1"

    expected_named_nodes = {
        "key1": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 0, 0, 7)),
        ),
        "key2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 0, 0, 7)),
        ),
        "somename": ValueNode(
            "arg1",
            info=NodeInfo(context=generate_context(0, 9, 0, 13)),
        ),
    }

    parser = runner(source, environment)

    compare_nodes_sequence(parser.unnamed_argument_nodes, [])
    compare_nodes_map(parser.named_argument_nodes, expected_named_nodes)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_process_arguments_alias_replacement_names_do_not_override():
    # Test that provided names do not override
    # existing named arguments with the same name.
    # In this test,
    # "arg1, @alias1, somename=somearg"
    # is replaced with
    # "arg1, somename=somearg, key1=value1, key2=value2"

    environment = Environment()
    environment["mau.parser.aliases"] = {
        "alias1": {
            "args": {"key1": "value1", "key2": "value2"},
            "names": ["somename"],
        }
    }

    source = "@alias1, arg1, somename=somearg"

    expected_unnamed_nodes = [
        ValueNode(
            "arg1",
            info=NodeInfo(context=generate_context(0, 9, 0, 13)),
        ),
    ]

    expected_named_nodes = {
        "key1": ValueNode(
            "value1",
            info=NodeInfo(context=generate_context(0, 0, 0, 7)),
        ),
        "key2": ValueNode(
            "value2",
            info=NodeInfo(context=generate_context(0, 0, 0, 7)),
        ),
        "somename": ValueNode(
            "somearg",
            info=NodeInfo(context=generate_context(0, 24, 0, 31)),
        ),
    }

    parser = runner(source, environment)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, expected_named_nodes)
    compare_nodes_sequence(parser.tag_nodes, [])
    assert parser.subtype is None


def test_process_arguments_alias_can_add_subtype():
    # Test that the replacement can provide a subtype.
    # In this test,
    # "arg1, @alias1"
    # is replaced with
    # "arg1, *subtype1"

    environment = Environment()
    environment["mau.parser.aliases"] = {"alias1": {"subtype": "subtype1"}}

    # These are out of order to check
    # that names are applied to actual
    # unnamed arguments and not to
    # the first argument.
    source = "@alias1, arg1"

    expected_unnamed_nodes = [
        ValueNode(
            "arg1",
            info=NodeInfo(context=generate_context(0, 9, 0, 13)),
        ),
    ]

    expected_subtype = ValueNode(
        "subtype1",
        info=NodeInfo(context=generate_context(0, 0, 0, 7)),
    )

    parser = runner(source, environment)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    compare_nodes(parser.subtype, expected_subtype)


def test_process_arguments_alias_does_not_replace_existing_subtype():
    # Test that the subtype provided by the replacement
    # does not override an existing subtype.
    # a subtype.
    # In this test,
    # "arg1, @alias1"
    # is replaced with
    # "arg1, *originalsubtype"

    environment = Environment()
    environment["mau.parser.aliases"] = {"alias1": {"subtype": "subtype1"}}

    # These are out of order to check
    # that names are applied to actual
    # unnamed arguments and not to
    # the first argument.
    source = "@alias1, arg1, *originalsubtype"

    expected_unnamed_nodes = [
        ValueNode(
            "arg1",
            info=NodeInfo(context=generate_context(0, 9, 0, 13)),
        ),
    ]

    expected_subtype = ValueNode(
        "originalsubtype",
        info=NodeInfo(context=generate_context(0, 15, 0, 31)),
    )

    parser = runner(source, environment)

    compare_nodes_sequence(parser.unnamed_argument_nodes, expected_unnamed_nodes)
    compare_nodes_map(parser.named_argument_nodes, {})
    compare_nodes_sequence(parser.tag_nodes, [])
    compare_nodes(parser.subtype, expected_subtype)


def test_arguments_empty():
    source = ""

    parser = runner(source)

    assert parser.arguments == NodeArguments(
        unnamed_args=[],
        named_args={},
        tags=[],
        internal_tags=[],
        subtype=None,
    )


def test_set_names_use_positional_names():
    source_unnamed_args = ["value1", "value2"]
    source_named_args: dict[str, str] = {}
    positional_names = ["attr1", "attr2"]

    expected_unnamed_args: list[str] = []
    expected_named_args = {"attr1": "value1", "attr2": "value2"}

    result_unnamed_args, result_named_args = set_names(
        source_unnamed_args, source_named_args, positional_names
    )

    assert result_unnamed_args == expected_unnamed_args
    assert result_named_args == expected_named_args


def test_set_names_named_wins_over_positional():
    # Named and unnamed arguments clash.
    # Here, attr1 is given as a named argument,
    # which wins over the positional arguments. So,
    # the only remaining positional name is attr2
    # which receives the first positional value (value1),
    # leaving value2 as a flag.

    source_unnamed_args = ["value1", "value2", "value3"]
    source_named_args: dict[str, str] = {"attr1": "value4"}
    positional_names = ["attr1", "attr2", "attr3"]

    expected_unnamed_args = ["value3"]
    expected_named_args = {
        "attr1": "value4",
        "attr2": "value1",
        "attr3": "value2",
    }

    result_unnamed_args, result_named_args = set_names(
        source_unnamed_args, source_named_args, positional_names
    )

    assert result_unnamed_args == expected_unnamed_args
    assert result_named_args == expected_named_args


def test_set_names_not_enough_positional_values():
    # Here, we give two positional names,
    # but there is only one value, so the
    # second name cannot be assigned.

    source_unnamed_args = ["value1"]
    source_named_args: dict[str, str] = {}
    positional_names = ["attr1", "attr2"]

    expected_unnamed_args: list[str] = []
    expected_named_args = {"attr1": "value1"}

    result_unnamed_args, result_named_args = set_names(
        source_unnamed_args, source_named_args, positional_names
    )

    assert result_unnamed_args == expected_unnamed_args
    assert result_named_args == expected_named_args


@patch("mau.nodes.node_arguments.set_names")
def test_arguments_set_names(mock_set_names):
    source = "value1, value2, key3=value3"

    # This is not important as long
    # as the function returns some values
    # with the correct format.
    mock_set_names.return_value = ([], {})

    parser = runner(source)
    parser.arguments.set_names(["attr1", "attr2"])

    mock_set_names.assert_called_with(
        ["value1", "value2"], {"key3": "value3"}, ["attr1", "attr2"]
    )


@patch("mau.parsers.arguments_parser.set_names")
def test_parser_set_names(mock_set_names):
    source = "value1, value2, key3=value3"

    # This is not important as long
    # as the function returns some values
    # with the correct format.
    mock_set_names.return_value = ([], {})

    parser = runner(source)
    parser.set_names(["attr1", "attr2"])

    compare_nodes_sequence(
        mock_set_names.call_args[0][0],
        [
            ValueNode(
                "value1",
                info=NodeInfo(context=generate_context(0, 0, 0, 6)),
            ),
            ValueNode(
                "value2",
                info=NodeInfo(context=generate_context(0, 8, 0, 14)),
            ),
        ],
    )

    compare_nodes_map(
        mock_set_names.call_args[0][1],
        {
            "key3": ValueNode(
                "value3",
                info=NodeInfo(context=generate_context(0, 21, 0, 27)),
            ),
        },
    )

    assert mock_set_names.call_args[0][2] == ["attr1", "attr2"]
