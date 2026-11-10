from unittest.mock import call, mock_open, patch

import pytest

from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.nodes.include import IncludeMauNode
from mau.nodes.inline import TextNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.paragraph import ParagraphLineNode, ParagraphNode
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import (
    compare_nodes_sequence,
    dedent,
    generate_context,
    init_parser_factory,
    parser_runner_factory,
)
from mau.text_buffer import Context

init_parser = init_parser_factory(DocumentLexer, DocumentParser)

runner = parser_runner_factory(DocumentLexer, DocumentParser)

MAU_ENVIRONMENT = {
    "mau": {
        "changelog": {
            "latest": "1.0.1",
            "versions": [
                {
                    "id": "1.0.0",
                    "date": "2026-11-04",
                    "changes": ["First change.", "Second change."],
                },
                {
                    "id": "1.0.1",
                    "date": "2026-11-05",
                    "changes": ["Third change."],
                },
            ],
        }
    }
}

CHANGELOG_TEMPLATE = dedent("""
{% for version in versions %}
[nobreak]
== Version {{ version.id }} ({{ version.date }})

{% for change in version.changes %}
* {{ change }}
{% endfor %}

{% endfor %}
""")

CHANGELOG_TEMPLATE_GLOBAL = dedent("""
{% for version in mau.changelog.versions %}
[nobreak]
== Version {{ version.id }} ({{ version.date }})

{% for change in version.changes %}
* {{ change }}
{% endfor %}

{% endfor %}
""")


def _text(node):
    # Join the values of the text
    # nodes contained in a node.
    return "".join(child.value for child in node.content)


def _check_changelog(include_node):
    # Check the structure created by
    # rendering the changelog template.
    content = include_node.content

    assert [node.type for node in content] == ["header", "list", "header", "list"]

    header_1, list_1, header_2, list_2 = content

    assert header_1.level == 2
    assert _text(header_1) == "Version 1.0.0 (2026-11-04)"
    assert header_1.arguments.unnamed_args == ["nobreak"]

    # The two changes of the first version
    # end up in a single list.
    assert [_text(item) for item in list_1.content] == [
        "First change.",
        "Second change.",
    ]

    assert _text(header_2) == "Version 1.0.1 (2026-11-05)"
    assert header_2.arguments.unnamed_args == ["nobreak"]

    assert [_text(item) for item in list_2.content] == ["Third change."]


# Test that the included file can be
# preprocessed by Jinja using the whole
# environment as template data and using
# hard coded global keys.
def test_include_mau_preprocess_jinja():
    source = """
    << mau:/path/to/it, preprocess=jinja
    """

    environment = Environment.from_dict(MAU_ENVIRONMENT)

    with patch(
        "builtins.open", mock_open(read_data=CHANGELOG_TEMPLATE_GLOBAL)
    ) as mock_file:
        parser = runner(source, environment)

    mock_file.assert_called_with("/path/to/it", "r", encoding="utf-8")

    assert len(parser.nodes) == 1

    include_node = parser.nodes[0]

    assert isinstance(include_node, IncludeMauNode)
    assert include_node.uri == "/path/to/it"

    # The preprocessing arguments are consumed
    # and are not stored in the node.
    assert include_node.arguments.named_args == {}

    _check_changelog(include_node)


# Test that the template data can be
# restricted to a part of the environment.
def test_include_mau_preprocess_jinja_with_data():
    source = """
    << mau:/path/to/it, preprocess=jinja, data=mau.changelog
    """

    environment = Environment.from_dict(MAU_ENVIRONMENT)

    with patch("builtins.open", mock_open(read_data=CHANGELOG_TEMPLATE)):
        parser = runner(source, environment)

    include_node = parser.nodes[0]

    assert include_node.arguments.named_args == {}

    _check_changelog(include_node)


# Test that Mau variables are replaced after the Jinja rendering.
def test_include_mau_preprocess_jinja_keeps_mau_variables():
    source = """
    :answer:42

    << mau:/path/to/it, preprocess=jinja
    """

    MAU_TEXT = dedent("""
    {{ mau.changelog.latest }}: the answer is {answer}.
    """)

    environment = Environment.from_dict(MAU_ENVIRONMENT)

    with patch("builtins.open", mock_open(read_data=MAU_TEXT)):
        parser = runner(source, environment)

    compare_nodes_sequence(
        parser.nodes,
        [
            IncludeMauNode(
                "/path/to/it",
                arguments=NodeArguments(
                    unnamed_args=[],
                    named_args={},
                    tags=[],
                    subtype=None,
                ),
                info=NodeInfo(
                    context=generate_context(3, 0, 3, 6),
                ),
                content=[
                    ParagraphNode(
                        content=[
                            ParagraphLineNode(
                                content=[
                                    TextNode(
                                        "1.0.1: the answer is 42.",
                                        info=NodeInfo(
                                            context=Context(0, 0, 0, 24, "/path/to/it")
                                        ),
                                    ),
                                ],
                                info=NodeInfo(
                                    context=Context(0, 0, 0, 30, "/path/to/it")
                                ),
                            ),
                        ],
                        info=NodeInfo(context=Context(0, 0, 0, 30, "/path/to/it")),
                    )
                ],
            ),
        ],
    )


# Test that call arguments are visible
# to the Jinja template.
def test_include_mau_preprocess_jinja_call_arguments():
    source = """
    << mau:/path/to/it, preprocess=jinja, call:answer=42
    """

    MAU_TEXT = dedent("""
    The answer is {{ answer }}.
    """)

    with patch("builtins.open", mock_open(read_data=MAU_TEXT)):
        parser = runner(source)

    assert _text(parser.nodes[0].content[0].content[0]) == "The answer is 42."


# Test that with pass_environment=false the template
# doesn't see the variables of the includer.
def test_include_mau_preprocess_jinja_prevent_environment_inclusion():
    source = """
    :answer:42

    << mau:/path/to/it, preprocess=jinja, pass_environment=false
    """

    MAU_TEXT = dedent("""
    The answer is {{ answer }}.
    """)

    with (
        pytest.raises(MauException) as exc,
        patch("builtins.open", mock_open(read_data=MAU_TEXT)),
    ):
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Jinja rendering error: 'answer' is undefined"
    assert exc.value.message.context == Context(0, 0, 0, 0, "/path/to/it")


# Test that the Jinja options come from
# the includer configuration, even when the
# environment is not passed to the included file.
def test_include_mau_preprocess_jinja_options_from_parent():
    source = """
    << mau:/path/to/it, preprocess=jinja, pass_environment=false, call:answer=42
    """

    MAU_TEXT = dedent("""
    The answer is [[ answer ]].
    """)

    environment = Environment.from_dict(
        {
            "parser": {
                "jinja": {
                    "options": {
                        "variable_start_string": "[[",
                        "variable_end_string": "]]",
                    }
                }
            },
        },
        "mau",
    )

    with patch("builtins.open", mock_open(read_data=MAU_TEXT)):
        parser = runner(source, environment)

    assert _text(parser.nodes[0].content[0].content[0]) == "The answer is 42."


# Test that Jinja errors point to the included file.
def test_include_mau_preprocess_jinja_syntax_error():
    source = """
    << mau:/path/to/it, preprocess=jinja
    """

    MAU_TEXT = dedent("""
    First line
    {% for x in %}
    {% endfor %}
    """)

    with (
        pytest.raises(MauException) as exc,
        patch("builtins.open", mock_open(read_data=MAU_TEXT)),
    ):
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text.startswith("Jinja syntax error:")
    assert exc.value.message.context == Context(1, 0, 1, 0, "/path/to/it")


# Test that errors in the data key point to
# the include directive.
def test_include_mau_preprocess_jinja_missing_data_key():
    source = """
    << mau:/path/to/it, preprocess=jinja, data=does.not.exist
    """

    with (
        pytest.raises(MauException) as exc,
        patch("builtins.open", mock_open(read_data="text")),
    ):
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Data key 'does.not.exist' not found in the Mau environment."
    )
    assert exc.value.message.context == generate_context(1, 0, 1, 6)


# Test that the data key must point to a mapping.
def test_include_mau_preprocess_jinja_data_key_not_a_mapping():
    source = """
    << mau:/path/to/it, preprocess=jinja, data=mau.changelog.versions
    """

    environment = Environment.from_dict(MAU_ENVIRONMENT)

    with (
        pytest.raises(MauException) as exc,
        patch("builtins.open", mock_open(read_data="text")),
    ):
        runner(source, environment)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Data key 'mau.changelog.versions' must point to a mapping, found list."
    )
    assert exc.value.message.context == generate_context(1, 0, 1, 6)


# Test that only available preprocessors can
# be requested. The check happens before the file
# is read, so no file is needed.
def test_include_mau_invalid_preprocessor():
    source = """
    << mau:/path/to/it, preprocess=notavailable
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Preprocessor 'notavailable' is not available."
    assert exc.value.message.context == generate_context(1, 0, 1, 6)


# Test that the data key cannot be used
# without the Jinja preprocessor. The check
# happens before the file read, so no
# file is needed.
def test_include_mau_data_requires_preprocess_jinja():
    source = """
    << mau:/path/to/it, data=mau.changelog
    """

    with pytest.raises(MauException) as exc:
        runner(source)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "The argument 'data' requires 'preprocess=jinja'."
    assert exc.value.message.context == generate_context(1, 0, 1, 6)
