import pytest

from mau.environment.environment import Environment
from mau.lexers.text_lexer import TextLexer
from mau.message import MauException, MauMessageType
from mau.nodes.inline import StyleNode, TextNode
from mau.nodes.node import NodeInfo
from mau.parsers.text_parser import TextParser
from mau.test_helpers import (
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_macro_control_if_equal():
    environment = Environment.from_dict({"flag": "true"})

    source = '[if:flag==true]("TRUE", "FALSE")'

    expected = [
        TextNode(
            "TRUE",
            info=NodeInfo(context=generate_context(0, 17, 0, 21)),
        )
    ]

    parser = runner(source, environment=environment)

    compare_nodes_sequence(parser.nodes, expected)


def test_macro_control_if_not_equal():
    environment = Environment.from_dict({"flag": "true"})

    source = '[if:flag==false]("TRUE", "FALSE")'

    expected = [
        TextNode(
            "FALSE",
            info=NodeInfo(context=generate_context(0, 26, 0, 31)),
        )
    ]

    parser = runner(source, environment=environment)

    compare_nodes_sequence(parser.nodes, expected)


def test_macro_control_missing_comparison_and_value():
    environment = Environment.from_dict({"flag": "true"})

    source = '[if:flag]("TRUE", "FALSE")'

    with pytest.raises(MauException) as exc:
        runner(source, environment=environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Wrong condition syntax: 'flag' (probably missing or incorrect comparison)."
    )


def test_macro_control_missing_variable():
    environment = Environment.from_dict({"flag": "true"})

    source = '[if]("TRUE", "FALSE")'

    with pytest.raises(MauException) as exc:
        runner(source, environment=environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Macro name 'if' must be in the form 'operator:condition'."
    )


def test_macro_control_undefined_variable():
    source = '[if:flag==true]("TRUE", "FALSE")'

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Variable 'flag' has not been defined."


def test_macro_control_invalid_test():
    environment = Environment.from_dict({"flag": "true"})

    source = '[if:flag<>true]("TRUE", "FALSE")'

    with pytest.raises(MauException) as exc:
        runner(source, environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Wrong condition syntax: 'flag<>true' (probably missing or incorrect comparison)."
    )


def test_macro_control_ifeval_true():
    # This test checks that the operator ifeval
    # uses the result as the name of a variable
    # and evaluates it before returning its output.

    environment = Environment.from_dict(
        {
            "flag": "true",
            "underscore": "_sometext_",
            "star": "*othertext*",
        }
    )

    source = "[ifeval:flag==true](underscore, star)"

    expected = [
        StyleNode(
            "underscore",
            content=[
                TextNode(
                    "sometext",
                    info=NodeInfo(context=generate_context(0, 21, 0, 29)),
                ),
            ],
            info=NodeInfo(context=generate_context(0, 20, 0, 30)),
        )
    ]

    parser = runner(source, environment=environment)

    compare_nodes_sequence(parser.nodes, expected)


def test_macro_control_ifeval_false():
    environment = Environment.from_dict(
        {
            "flag": "true",
            "underscore": "_sometext_",
            "star": "*othertext*",
        }
    )

    source = "[ifeval:flag==false](underscore, star)"

    expected = [
        StyleNode(
            "star",
            content=[
                TextNode(
                    "othertext",
                    info=NodeInfo(context=generate_context(0, 34, 0, 43)),
                ),
            ],
            info=NodeInfo(context=generate_context(0, 33, 0, 44)),
        )
    ]

    parser = runner(source, environment=environment)

    compare_nodes_sequence(parser.nodes, expected)


def test_macro_control_ifeval_false_delayed_evaluation():
    environment = Environment.from_dict(
        {
            "flag": "true",
            "style": "_sometext_",
            "header": "[header](notexists)",
        }
    )

    source = "[ifeval:flag==true](style, header)"

    expected = [
        StyleNode(
            "underscore",
            content=[
                TextNode(
                    "sometext",
                    info=NodeInfo(context=generate_context(0, 21, 0, 29)),
                ),
            ],
            info=NodeInfo(context=generate_context(0, 20, 0, 30)),
        )
    ]

    parser = runner(source, environment=environment)

    compare_nodes_sequence(parser.nodes, expected)


def test_macro_control_ifeval_true_delayed_evaluation():
    environment = Environment.from_dict(
        {
            "flag": "true",
            "style": "_sometext_",
            "header": "[header](notexists)",
        }
    )

    source = "[ifeval:flag==false](header, style)"

    expected = [
        StyleNode(
            "underscore",
            content=[
                TextNode(
                    "sometext",
                    info=NodeInfo(context=generate_context(0, 30, 0, 38)),
                ),
            ],
            info=NodeInfo(context=generate_context(0, 29, 0, 39)),
        )
    ]

    parser = runner(source, environment=environment)

    compare_nodes_sequence(parser.nodes, expected)


def test_macro_control_ifeval_undefined_variable():
    environment = Environment.from_dict({"flag": "false"})

    source = "[ifeval:flag==true](var)"

    with pytest.raises(MauException) as exc:
        runner(source, environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "The test result is negative but no value has been defined for that case."
    )


def test_macro_control_ifeval_true_not_defined():
    environment = Environment.from_dict(
        {
            "flag": "true",
            "star": "*othertext*",
        }
    )

    source = "[ifeval:flag==true](underscore, star)"

    with pytest.raises(MauException) as exc:
        runner(source, environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Variable 'underscore' has not been defined."


def test_macro_control_ifeval_false_not_defined():
    environment = Environment.from_dict(
        {
            "flag": "true",
            "underscore": "_sometext_",
        }
    )

    source = "[ifeval:flag==false](underscore, star)"

    with pytest.raises(MauException) as exc:
        runner(source, environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Variable 'star' has not been defined."


def test_macro_control_default_false():
    environment = Environment.from_dict({"flag": "true"})

    source = '[if:flag==false]("TRUE")'

    nodes = runner(source, environment=environment).nodes

    assert nodes == []


def test_macro_control_without_true_case():
    source = "[if:flag==false]()"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Control macro is missing the mandatory value for the true case."
    )
    assert exc.value.message.context == generate_context(0, 0, 0, 18)
