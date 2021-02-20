import pytest

from mau.parsers.preprocess_variables_parser import (
    PreprocessVariablesParser,
    PreprocessError,
)

from tests.helpers import listasdict, init_parser_factory, dedent

init_parser = init_parser_factory(PreprocessVariablesParser)


def test_plain_text():
    p = init_parser("This is text", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is text\n",
        }
    ]


def test_replace_variable():
    p = init_parser("This is number {attr}", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is number 5\n",
        }
    ]


def test_replace_variable_with_namespace():
    p = init_parser("This is number {config.attr}", {"config": {"attr": "5"}})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is number 5\n",
        }
    ]


def test_replace_boolean():
    p = init_parser("This flag is {flag}", {"flag": True})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This flag is True\n",
        }
    ]


def test_escape_curly_braces():
    p = init_parser(r"This is \{attr\}", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is {attr}\n",
        }
    ]


def test_curly_braces_in_verbatim():
    p = init_parser("This is `{attr}`", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is `{attr}`\n",
        }
    ]


def test_open_verbatim():
    p = init_parser("This is `{attr}", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is `5\n",
        }
    ]


def test_open_curly():
    p = init_parser("This is {attr", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is {attr\n",
        }
    ]


def test_escape_curly_braces_in_verbatim():
    p = init_parser(r"This is `\{attr\}`", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is `\\{attr\\}`\n",
        }
    ]


def test_escape_other_chars():
    p = init_parser(r"This \_is\_ \text", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This \\_is\\_ \\text\n",
        }
    ]


def test_curly_braces_in_escaped_verbatim():
    p = init_parser(r"This is \`{attr}\`", {"attr": "5"})
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is \\`5\\`\n",
        }
    ]


def test_variable_not_existing():
    p = init_parser("This is number {attr}", {})

    with pytest.raises(PreprocessError):
        p.parse()


def test_variables_can_contain_markers():
    p = init_parser(
        dedent(
            """
            A very {bold} text
            Some code: {dictdef}
            """
        ),
        {"bold": "*bold*", "dictdef": "`adict = {'a':5}`"},
    )
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "A very *bold* text\nSome code: `adict = {'a':5}`\n",
        }
    ]


def test_escape_backtick():
    p = init_parser(r"This is `\``")
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "text",
            "value": "This is `\``\n",
        }
    ]
