import pytest

from mau.environment.environment import Environment
from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer
from mau.message import MauException, MauMessageType
from mau.nodes.inline import TextNode
from mau.nodes.node import NodeInfo
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.test_helpers import (
    compare_asdict_object,
    compare_nodes_sequence,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)
from mau.token import Token, TokenType

init_parser = init_parser_factory(PreprocessVariablesLexer, PreprocessVariablesParser)
runner = parser_runner_factory(PreprocessVariablesLexer, PreprocessVariablesParser)


def test_empty():
    source = ""

    parser = runner(source)

    assert parser.nodes == []
    assert parser.get_processed_text() == Token.generate(TokenType.TEXT)


def test_plain_text_with_no_variables():
    source = "This is text"

    expected_text = "This is text"
    expected = [
        TextNode(
            expected_text,
            info=NodeInfo(context=generate_context(0, 0, 0, 12)),
        )
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            expected_text,
            generate_context(0, 0, 0, 12),
        ),
    )


def test_plain_text_with_variables():
    environment = Environment.from_dict({"attr": "5"})
    source = "This is text"

    expected_text = "This is text"
    expected = [
        TextNode(
            expected_text,
            info=NodeInfo(context=generate_context(0, 0, 0, 12)),
        )
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            expected_text,
            generate_context(0, 0, 0, 12),
        ),
    )


def test_replace_variable():
    environment = Environment.from_dict({"attr": "5"})
    source = "This is number {attr}"

    expected = [
        TextNode(
            "This is number ",
            info=NodeInfo(context=generate_context(0, 0, 0, 15)),
        ),
        TextNode(
            "5",
            info=NodeInfo(context=generate_context(0, 15, 0, 21)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "This is number 5",
            generate_context(0, 0, 0, 21),
        ),
    )


def test_replace_variable_coerce_string_type():
    environment = Environment.from_dict({"attr": 5})
    source = "This is number {attr}"

    expected = [
        TextNode(
            "This is number ",
            info=NodeInfo(context=generate_context(0, 0, 0, 15)),
        ),
        TextNode(
            "5",
            info=NodeInfo(context=generate_context(0, 15, 0, 21)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "This is number 5",
            generate_context(0, 0, 0, 21),
        ),
    )


def test_manage_unclosed_curly_braces():
    environment = Environment.from_dict({"attr": "5"})
    source = "This is {attr"

    expected = [
        TextNode(
            "This is ",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
        TextNode(
            "{",
            info=NodeInfo(context=generate_context(0, 8, 0, 9)),
        ),
        TextNode(
            "attr",
            info=NodeInfo(context=generate_context(0, 9, 0, 13)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "This is {attr",
            generate_context(0, 0, 0, 13),
        ),
    )


def test_replace_variable_with_namespace():
    environment = Environment.from_dict({"app": {"attr": "5"}})
    source = "This is number {app.attr}"

    expected = [
        TextNode(
            "This is number ",
            info=NodeInfo(context=generate_context(0, 0, 0, 15)),
        ),
        TextNode(
            "5",
            info=NodeInfo(context=generate_context(0, 15, 0, 25)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "This is number 5",
            generate_context(0, 0, 0, 25),
        ),
    )


def test_escape_curly_braces():
    environment = Environment.from_dict({"attr": "5"})
    source = r"This is \{attr\}"

    expected = [
        TextNode(
            "This is ",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
        TextNode(
            "{",
            info=NodeInfo(context=generate_context(0, 8, 0, 10)),
        ),
        TextNode(
            "attr",
            info=NodeInfo(context=generate_context(0, 10, 0, 14)),
        ),
        TextNode(
            "}",
            info=NodeInfo(context=generate_context(0, 14, 0, 16)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "This is {attr}",
            generate_context(0, 0, 0, 16),
        ),
    )


def test_escape_curly_braces_with_double_braces():
    environment = Environment.from_dict({"attr": "5"})
    source = r"This is {{attr}}"

    expected = [
        TextNode(
            "This is ",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
        TextNode(
            "{attr}",
            info=NodeInfo(context=generate_context(0, 8, 0, 16)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "This is {attr}",
            generate_context(0, 0, 0, 16),
        ),
    )


def test_unclosed_double_braces():
    source = r"This is {{attr}"

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Incomplete variable declaration '{attr'. Variable names cannot contain curly braces."
    )


def test_curly_braces_in_verbatim():
    environment = Environment.from_dict({"attr": "5"})
    source = "This is `{attr}`"

    expected = [
        TextNode(
            "This is ",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
        TextNode(
            "`{attr}`",
            info=NodeInfo(context=generate_context(0, 8, 0, 16)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "This is `{attr}`",
            generate_context(0, 0, 0, 16),
        ),
    )


def test_open_verbatim():
    environment = Environment.from_dict({"attr": "5"})
    source = "This is `{attr}"

    expected = [
        TextNode(
            "This is ",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
        TextNode(
            "`",
            info=NodeInfo(context=generate_context(0, 8, 0, 9)),
        ),
        TextNode(
            "5",
            info=NodeInfo(context=generate_context(0, 9, 0, 15)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "This is `5",
            generate_context(0, 0, 0, 15),
        ),
    )


def test_escape_curly_braces_in_verbatim():
    environment = Environment.from_dict({"attr": "5"})
    source = r"This is `\{attr\}`"

    expected = [
        TextNode(
            r"This is ",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
        TextNode(
            r"`\{attr\}`",
            info=NodeInfo(context=generate_context(0, 8, 0, 18)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            r"This is `\{attr\}`",
            generate_context(0, 0, 0, 18),
        ),
    )


def test_escape_other_chars():
    environment = Environment.from_dict({"attr": "5"})
    source = r"This \_is\_ \text"

    expected = [
        TextNode(
            r"This ",
            info=NodeInfo(context=generate_context(0, 0, 0, 5)),
        ),
        TextNode(
            r"\_is",
            info=NodeInfo(context=generate_context(0, 5, 0, 9)),
        ),
        TextNode(
            r"\_ ",
            info=NodeInfo(context=generate_context(0, 9, 0, 12)),
        ),
        TextNode(
            r"\text",
            info=NodeInfo(context=generate_context(0, 12, 0, 17)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            r"This \_is\_ \text",
            generate_context(0, 0, 0, 17),
        ),
    )


def test_curly_braces_in_escaped_verbatim():
    environment = Environment.from_dict({"attr": "5"})
    source = r"This is \`{attr}\`"

    expected = [
        TextNode(
            r"This is ",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
        TextNode(
            r"\`",
            info=NodeInfo(context=generate_context(0, 8, 0, 10)),
        ),
        TextNode(
            r"5",
            info=NodeInfo(context=generate_context(0, 10, 0, 16)),
        ),
        TextNode(
            r"\`",
            info=NodeInfo(context=generate_context(0, 16, 0, 18)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            r"This is \`5\`",
            generate_context(0, 0, 0, 18),
        ),
    )


def test_variable_not_existing():
    environment = Environment()
    source = "This is number {attr}"

    with pytest.raises(MauException) as exc:
        runner(source, environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Variable 'attr' has not been defined."
    assert exc.value.message.context == generate_context(0, 15, 0, 21)


def test_variables_can_contain_markers():
    environment = Environment.from_dict(
        {"bold": "*bold*", "dictdef": "`adict = {'a':5}`"}
    )
    source = "A very {bold} text. Some code: {dictdef}"

    expected = [
        TextNode(
            "A very ",
            info=NodeInfo(context=generate_context(0, 0, 0, 7)),
        ),
        TextNode(
            "*bold*",
            info=NodeInfo(context=generate_context(0, 7, 0, 13)),
        ),
        TextNode(
            " text. Some code: ",
            info=NodeInfo(context=generate_context(0, 13, 0, 31)),
        ),
        TextNode(
            "`adict = {'a':5}`",
            info=NodeInfo(context=generate_context(0, 31, 0, 40)),
        ),
    ]

    parser = runner(source, environment)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            "A very *bold* text. Some code: `adict = {'a':5}`",
            generate_context(0, 0, 0, 40),
        ),
    )


def test_escape_backtick():
    source = r"This is `\``"

    expected = [
        TextNode(
            "This is ",
            info=NodeInfo(context=generate_context(0, 0, 0, 8)),
        ),
        TextNode(
            r"`\``",
            info=NodeInfo(context=generate_context(0, 8, 0, 12)),
        ),
    ]

    parser = runner(source)

    compare_nodes_sequence(parser.nodes, expected)
    compare_asdict_object(
        parser.get_processed_text(),
        Token(
            TokenType.TEXT,
            r"This is `\``",
            generate_context(0, 0, 0, 12),
        ),
    )
