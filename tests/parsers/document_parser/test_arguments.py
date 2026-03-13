import pytest

from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.nodes.node_arguments import NodeArguments
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_arguments():
    source = """
    [attr1, attr2, #tag1, *subtype1, key1=value1]
    """

    parser = runner(source)

    # This checks that attributes are correctly stored.
    assert parser.arguments_buffer.pop() == NodeArguments(
        unnamed_args=["attr1", "attr2"],
        named_args={"key1": "value1"},
        tags=["tag1"],
        subtype="subtype1",
    )


def test_arguments_empty():
    source = """
    []
    """

    parser = runner(source)

    assert parser.arguments_buffer.pop().asdict() == NodeArguments().asdict()


def test_arguments_multiple_subtypes():
    source = """
    [*subtype1, *subtype2]
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Multiple nodes with prefix '*' detected."


def test_arguments_multiple_aliases():
    source = """
    [@alias1, @alias2]
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Multiple nodes with prefix '@' detected."


def test_arguments_support_variables_with_syntax():
    environment = Environment.from_dict(
        {
            "arg": "arg1",
            "keyvalue": "key1=value1",
            "tag_with_prefix": "#tag1",
            "subtype_with_prefix": "*subtype1",
        }
    )

    source = """
    [{arg}, {tag_with_prefix}, {subtype_with_prefix}, {keyvalue}]
    """

    parser = runner(source, environment)

    assert parser.arguments_buffer.pop() == NodeArguments(
        unnamed_args=["arg1"],
        named_args={"key1": "value1"},
        tags=["tag1"],
        internal_tags=[],
        subtype="subtype1",
    )


def test_arguments_support_variables_without_syntax():
    environment = Environment.from_dict(
        {
            "arg": "arg1",
            "key": "key1",
            "value": "value1",
            "tag_without_prefix": "tag1",
            "subtype_without_prefix": "subtype1",
        }
    )

    source = """
    [{arg}, #{tag_without_prefix}, *{subtype_without_prefix}, {key}={value}]
    """

    parser = runner(source, environment)

    assert parser.arguments_buffer.pop() == NodeArguments(
        unnamed_args=["arg1"],
        named_args={"key1": "value1"},
        tags=["tag1"],
        internal_tags=[],
        subtype="subtype1",
    )


def test_arguments_support_variables_with_commas():
    environment = Environment.from_dict(
        {
            "unnamed_args": "arg1, arg2, #tag1",
            "named_args": "key1=value1",
        }
    )

    source = """
    [{unnamed_args}, otherarg, {named_args}, otherkey=othervalue]
    """

    parser = runner(source, environment)

    assert parser.arguments_buffer.pop() == NodeArguments(
        unnamed_args=["arg1", "arg2", "otherarg"],
        named_args={"key1": "value1", "otherkey": "othervalue"},
        tags=["tag1"],
        internal_tags=[],
        subtype=None,
    )
