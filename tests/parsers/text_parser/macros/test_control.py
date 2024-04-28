import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.text_lexer import TextLexer
from mau.nodes.inline import SentenceNode, StyleNode, TextNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_control_if_true():
    environment = Environment({"flag": True})

    source = '[@if:flag:&true]("TRUE", "FALSE")'

    expected = [
        SentenceNode(
            children=[TextNode("TRUE")],
        ),
    ]

    assert runner(source, environment=environment).nodes == expected


def test_control_if_false():
    environment = Environment({"flag": True})

    source = '[@if:flag:&false]("TRUE", "FALSE")'

    expected = [
        SentenceNode(
            children=[TextNode("FALSE")],
        ),
    ]

    assert runner(source, environment=environment).nodes == expected


def test_control_if_equal():
    environment = Environment({"flag": "42"})

    source = '[@if:flag:=42]("TRUE", "FALSE")'

    expected = [
        SentenceNode(
            children=[TextNode("TRUE")],
        ),
    ]

    assert runner(source, environment=environment).nodes == expected


def test_control_if_not_equal():
    environment = Environment({"flag": "42"})

    source = '[@if:flag:!=42]("TRUE", "FALSE")'

    expected = [
        SentenceNode(
            children=[TextNode("FALSE")],
        ),
    ]

    assert runner(source, environment=environment).nodes == expected


def test_control_wrong_name_format():
    source = '[@if:flag]("TRUE", "FALSE")'

    with pytest.raises(MauErrorException):
        runner(source)


def test_control_unsupported_operator():
    source = '[@something:flag:&true]("TRUE", "FALSE")'

    with pytest.raises(MauErrorException):
        runner(source)


def test_control_undefined_variable():
    source = '[@if:flag:&true]("TRUE", "FALSE")'

    with pytest.raises(MauErrorException):
        runner(source)


def test_control_invalid_boolean():
    environment = Environment({"flag": "42"})

    source = '[@if:flag:&something]("TRUE", "FALSE")'

    with pytest.raises(MauErrorException):
        runner(source, environment)


def test_control_invalid_test():
    environment = Environment({"flag": "42"})

    source = '[@if:flag:-something]("TRUE", "FALSE")'

    with pytest.raises(MauErrorException):
        runner(source, environment)


def test_macro_ifeval_true():
    environment = Environment(
        {
            "flag": True,
            "underscore": "_sometext_",
            "star": "*othertext*",
        }
    )

    source = "[@ifeval:flag:&true](underscore, star)"

    expected = [
        SentenceNode(
            children=[
                StyleNode(
                    value="underscore",
                    children=[
                        TextNode("sometext"),
                    ],
                )
            ],
        ),
    ]

    assert runner(source, environment=environment).nodes == expected


def test_macro_ifeval_false():
    environment = Environment(
        {
            "flag": True,
            "underscore": "_sometext_",
            "star": "*othertext*",
        }
    )

    source = "[@ifeval:flag:&false](underscore, star)"

    expected = [
        SentenceNode(
            children=[
                StyleNode(
                    value="star",
                    children=[
                        TextNode("othertext"),
                    ],
                )
            ],
        ),
    ]

    assert runner(source, environment=environment).nodes == expected


def test_macro_ifeval_false_is_not_evaluated():
    environment = Environment(
        {
            "flag": True,
            "style": "_sometext_",
            "header": "[header](notexists)",
        }
    )

    source = "[@ifeval:flag:&true](style, header)"

    expected = [
        SentenceNode(
            children=[
                StyleNode(
                    value="underscore",
                    children=[
                        TextNode("sometext"),
                    ],
                )
            ],
        ),
    ]

    assert runner(source, environment=environment).nodes == expected


def test_macro_ifeval_true_is_not_evaluated():
    environment = Environment(
        {
            "flag": True,
            "style": "_sometext_",
            "header": "[header](notexists)",
        }
    )

    source = "[@ifeval:flag:&false](header, style)"

    expected = [
        SentenceNode(
            children=[
                StyleNode(
                    value="underscore",
                    children=[
                        TextNode("sometext"),
                    ],
                )
            ],
        ),
    ]

    assert runner(source, environment=environment).nodes == expected


def test_macro_ifeval_true_not_defined():
    environment = Environment(
        {
            "flag": True,
            "star": "*othertext*",
        }
    )

    source = "[@ifeval:flag:&true](underscore, star)"

    with pytest.raises(MauErrorException):
        runner(source, environment)


def test_macro_ifeval_false_not_defined():
    environment = Environment(
        {
            "flag": True,
            "underscore": "_sometext_",
        }
    )

    source = "[@ifeval:flag:&false](underscore, star)"

    with pytest.raises(MauErrorException):
        runner(source, environment)
