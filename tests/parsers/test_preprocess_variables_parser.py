import pytest
from mau.environment.environment import Environment
from mau.errors import MauErrorException
from mau.lexers.preprocess_variables_lexer import PreprocessVariablesLexer
from mau.nodes.inline import TextNode
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(PreprocessVariablesLexer, PreprocessVariablesParser)
runner = parser_runner_factory(PreprocessVariablesLexer, PreprocessVariablesParser)


def test_plain_text_with_no_variables():
    source = "This is text"

    assert runner(source).nodes == [TextNode("This is text")]


def test_plain_text_with_variables():
    source = "This is text"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode("This is text")]


def test_replace_variable():
    source = "This is number {attr}"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode("This is number 5")]


def test_manage_unclosed_curly_braces():
    source = "This is {attr"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode("This is {attr")]


def test_replace_variable_with_namespace():
    source = "This is number {app.attr}"
    result = runner(
        source,
        environment=Environment({"app": {"attr": "5"}}),
    )

    assert result.nodes == [TextNode("This is number 5")]


def test_replace_boolean():
    result = runner("This flag is {flag}", environment=Environment({"flag": True}))

    assert result.nodes == [TextNode("This flag is ")]


def test_escape_curly_braces():
    source = r"This is \{attr\}"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode("This is {attr}")]


def test_curly_braces_in_verbatim():
    source = "This is `{attr}`"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode("This is `{attr}`")]


def test_open_verbatim():
    source = "This is `{attr}"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode("This is `5")]


def test_escape_curly_braces_in_verbatim():
    source = r"This is `\{attr\}`"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode(r"This is `\{attr\}`")]


def test_escape_other_chars():
    source = r"This \_is\_ \text"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode(r"This \_is\_ \text")]


def test_curly_braces_in_escaped_verbatim():
    source = r"This is \`{attr}\`"
    result = runner(source, environment=Environment({"attr": "5"}))

    assert result.nodes == [TextNode(r"This is \`5\`")]


def test_variable_not_existing():
    source = "This is number {attr}"

    with pytest.raises(MauErrorException):
        runner(source, environment={})


def test_variables_can_contain_markers():
    source = "A very {bold} text. Some code: {dictdef}"
    result = runner(
        source,
        environment=Environment({"bold": "*bold*", "dictdef": "`adict = {'a':5}`"}),
    )

    assert result.nodes == [
        TextNode("A very *bold* text. Some code: `adict = {'a':5}`")
    ]


def test_escape_backtick():
    result = runner(r"This is `\``")

    assert result.nodes == [TextNode(r"This is `\``")]
