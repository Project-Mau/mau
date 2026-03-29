import pytest

from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.nodes.include import IncludeNode
from mau.nodes.inline import TextNode
from mau.nodes.label import LabelNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    check_parent,
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def test_include_content_inline_arguments():
    source = """
    << ctype1:/path/to/it, /another/path, #tag1, *subtype1, key1=value1
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeNode(
                "ctype1",
                arguments=NodeArguments(
                    unnamed_args=["/path/to/it", "/another/path"],
                    named_args={"key1": "value1"},
                    tags=["tag1"],
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(1, 0, 1, 9),
                ),
            ),
        ],
    )


def test_include_content_without_arguments():
    source = """
    << ctype1
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeNode(
                "ctype1",
                arguments=NodeArguments(
                    unnamed_args=[],
                    named_args={},
                    tags=[],
                    subtype=None,
                ),
                info=NodeInfo(
                    context=generate_context(1, 0, 1, 9),
                ),
            ),
        ],
    )


def test_include_inline_arguments_support_variables():
    environment = Environment.from_dict(
        {
            "paths": "/path/to/it, /another/path",
            "keyvalue": "key1=value1",
            "tag_with_prefix": "#tag1",
            "subtype_with_prefix": "*subtype1",
        }
    )

    source = """
    << ctype1:{paths}, {tag_with_prefix}, {subtype_with_prefix}, {keyvalue}
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeNode(
                "ctype1",
                arguments=NodeArguments(
                    unnamed_args=["/path/to/it", "/another/path"],
                    named_args={"key1": "value1"},
                    tags=["tag1"],
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(1, 0, 1, 9),
                ),
            ),
        ],
    )


def test_include_content_boxed_arguments():
    source = """
    [/path/to/it, /another/path, #tag1, *subtype1, key1=value1]
    << ctype1
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeNode(
                "ctype1",
                arguments=NodeArguments(
                    unnamed_args=["/path/to/it", "/another/path"],
                    named_args={"key1": "value1"},
                    tags=["tag1"],
                    subtype="subtype1",
                ),
                info=NodeInfo(
                    context=generate_context(2, 0, 2, 9),
                ),
            ),
        ],
    )


def test_include_content_boxed_and_inline_arguments_are_forbidden():
    source = """
    [/path/to/it]
    << ctype1:/another/path
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Syntax error. You cannot specify both boxed and inline arguments."
    )
    assert exc.value.message.context == generate_context(2, 0, 2, 9)


def test_include_content_with_label():
    source = """
    . A title
    << ctype1:/path/to/it,/another/path
    """

    parser = runner(source)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeNode(
                "ctype1",
                arguments=NodeArguments(
                    unnamed_args=["/path/to/it", "/another/path"],
                    named_args={},
                    tags=[],
                    subtype=None,
                ),
                labels={
                    "title": LabelNode(
                        "title",
                        content=[
                            TextNode(
                                "A title",
                                info=NodeInfo(context=generate_context(1, 2, 1, 9)),
                            )
                        ],
                    ),
                },
                info=NodeInfo(context=generate_context(2, 0, 2, 9)),
            )
        ],
    )


def test_header_uses_control_positive():
    environment = Environment()
    environment["answer"] = "42"

    source = """
    @if answer==42
    << ctype1:/path/to/it
    """

    parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeNode(
                "ctype1",
                arguments=NodeArguments(
                    unnamed_args=["/path/to/it"],
                    named_args={},
                    tags=[],
                    subtype=None,
                ),
                info=NodeInfo(
                    context=generate_context(2, 0, 2, 9),
                ),
            ),
        ],
    )

    assert parser.control_buffer.pop() is None


def test_header_uses_control_negative():
    environment = Environment()
    environment["answer"] = "24"

    source = """
    @if answer==42
    << ctype1:/path/to/it
    """

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, [])


def test_include_parenthood():
    source = """
    << ctype1:/path/to/it
    """

    parser = runner(source)

    document_node = parser.output.document

    # All parser nodes must be
    # children of the document node.
    check_parent(document_node, parser.nodes)


def test_list_parenthood_labels():
    source = """
    . A label
    .role Another label
    << ctype1:/path/to/it
    """

    parser = runner(source)

    include_node = parser.nodes[0]
    label_title = include_node.labels["title"]
    label_role = include_node.labels["role"]

    # Each label must be a child of the
    # include node it has been assigned to.
    check_parent(include_node, [label_title])
    check_parent(include_node, [label_role])
    check_parent(label_title, label_title.content)
    check_parent(label_role, label_role.content)
