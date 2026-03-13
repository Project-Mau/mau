from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import TextNode
from mau.nodes.macro import MacroNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.parsers.text_parser import TextParser
from mau.test_helpers import (
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_generic_macro():
    source = "[macroname](arg1,arg2)"

    expected = [
        MacroNode(
            "macroname",
            arguments=NodeArguments(
                unnamed_args=["arg1", "arg2"],
                named_args={},
                tags=[],
                subtype=None,
            ),
            info=NodeInfo(context=generate_context(0, 0, 0, 22)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)


def test_generic_macro_incomplete():
    source = "[macroname](arg1"

    expected = [
        TextNode(
            "[macroname](arg1",
            info=NodeInfo(context=generate_context(0, 0, 0, 16)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)


def test_generic_macro_supports_all_argument_types():
    source = "[macroname](arg1, #tag1, *subtype1, key1=value1)"

    expected = [
        MacroNode(
            "macroname",
            arguments=NodeArguments(
                unnamed_args=["arg1"],
                named_args={"key1": "value1"},
                tags=["tag1"],
                subtype="subtype1",
            ),
            info=NodeInfo(context=generate_context(0, 0, 0, 48)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)


def test_generic_macro_without_arguments():
    source = "[macroname]()"

    expected = [
        MacroNode(
            "macroname",
            arguments=NodeArguments(),
            info=NodeInfo(context=generate_context(0, 0, 0, 13)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)
