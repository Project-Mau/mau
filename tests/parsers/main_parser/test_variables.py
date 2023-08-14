from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import SentenceNode, StyleNode, TextNode
from mau.nodes.page import ParagraphNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_parse_variable_definition_without_value_is_loaded_as_boolean():
    source = ":attr:"
    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.asdict() == {"attr": True}


def test_parse_variable_definition_without_value_can_be_negated():
    source = ":!attr:"
    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.asdict() == {"attr": False}


def test_parse_variable_definition_negative_flag_ignores_value():
    source = ":!attr:42"
    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.asdict() == {"attr": False}


def test_parse_variable_definition_with_value_is_loaded():
    source = ":attr:42"
    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.asdict() == {"attr": "42"}


def test_parse_variable_definition_value_can_be_any_text():
    source = ":attr:[footnote](http://some.domain/path)"
    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.asdict() == {
        "attr": "[footnote](http://some.domain/path)",
    }


def test_parse_variable_definition_with_namespace():
    source = ":meta.attr:42"
    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.asdict() == {"meta": {"attr": "42"}}


def test_parse_variable_definition_with_multiple_dots():
    source = ":meta.category.attr:42"
    parser = runner(source)

    assert parser.nodes == []
    assert parser.environment.asdict() == {"meta": {"category": {"attr": "42"}}}


def test_variable_replacement():
    source = """
    :answer:42

    The answer is {answer}
    """

    parser = runner(source)

    assert parser.nodes == [
        ParagraphNode(
            SentenceNode(
                [TextNode("The answer is 42")],
            )
        )
    ]


def test_variable_replacement_with_namespace():
    source = """
    :mau.answer:42

    The answer is {mau.answer}
    """

    parser = runner(source)

    assert parser.nodes == [
        ParagraphNode(
            SentenceNode(
                [TextNode("The answer is 42")],
            )
        )
    ]


def test_variable_definition_escape():
    source = r"""
    \:answer:42
    """

    parser = runner(source)

    assert parser.nodes == [
        ParagraphNode(
            SentenceNode(
                [TextNode(":answer:42")],
            )
        )
    ]


def test_skip_variable_replacement():
    source = r"""
    :answer:42

    The answer is \{answer\}
    """

    parser = runner(source)

    assert parser.nodes == [
        ParagraphNode(
            SentenceNode(
                [TextNode("The answer is {answer}")],
            )
        )
    ]


def test_variables_are_preprocessed():
    source = r"""
    :important:*IMPORTANT*

    This is {important}
    """

    parser = runner(source)

    assert parser.nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This is "),
                    StyleNode(
                        "star",
                        SentenceNode(
                            [
                                TextNode("IMPORTANT"),
                            ]
                        ),
                    ),
                ],
            )
        )
    ]
