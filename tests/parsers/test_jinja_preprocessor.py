import datetime

import pytest

from mau.environment.environment import Environment
from mau.message import MauException, MauMessageType
from mau.parsers.jinja_preprocessor import render_jinja_source
from mau.test_helpers import dedent, generate_context
from mau.text_buffer import Context

MAU_ENVIRONMENT = {
    "mau": {
        "changelog": {
            "latest": "1.0.1",
            "versions": [
                {
                    "id": "1.0.0",
                    "date": datetime.date(2026, 11, 4),
                    "changes": ["First change", "Second change."],
                },
                {
                    "id": "1.0.1",
                    "date": datetime.date(2026, 11, 5),
                    "changes": ["Third change"],
                },
            ],
        }
    }
}


def test_render_plain_text_is_unchanged():
    source = "This is *Mau* text with a {variable}.\n"

    assert render_jinja_source(source, Environment()) == source


# Test that Mau files can be rendered
# using the whole environment and hard
# coding global keys in the template.
def test_render_template_using_global_keys():
    # The Mau environment.
    environment = Environment.from_dict(MAU_ENVIRONMENT)

    # The Mau source that
    # uses global keys.
    source = "Version {{ mau.changelog.latest }}"

    # Render the Mau source as
    # a Jinja template.
    result = render_jinja_source(source, environment)

    assert result == "Version 1.0.1"


# Test that Mau files can be rendered
# using part of the environment, with
# local keys in the template.
def test_render_template_using_local_keys():
    # The Mau environment.
    environment = Environment.from_dict(MAU_ENVIRONMENT)

    # The Mau source that
    # uses global keys.
    source = "Version {{ latest }}"

    # Render the Mau source as
    # a Jinja template.
    result = render_jinja_source(source, environment, data_key="mau.changelog")

    assert result == "Version 1.0.1"


# Test that the Jinja preprocessor doesn't
# add unwanted spaces.
def test_render_loop_over_list_from_environment():
    environment = Environment.from_dict(MAU_ENVIRONMENT)

    source = dedent("""
    {% for version in mau.changelog.versions %}
    [nobreak]
    == Version {{ version.id }} ({{ version.date }})

    {% for change in version.changes %}
    * {{ change }}
    {% endfor %}

    {% endfor %}
    """)

    expected = (
        "[nobreak]\n"
        "== Version 1.0.0 (2026-11-04)\n"
        "\n"
        "* First change\n"
        "* Second change.\n"
        "\n"
        "[nobreak]\n"
        "== Version 1.0.1 (2026-11-05)\n"
        "\n"
        "* Third change\n"
        "\n"
    )

    assert render_jinja_source(source, environment) == expected


def test_render_indented_block_tags_leave_no_indentation():
    environment = Environment.from_dict({"items": ["a", "b"]})

    source = "    {% for item in items %}\n* {{ item }}\n    {% endfor %}\n"

    assert render_jinja_source(source, environment) == "* a\n* b\n"


def test_render_keeps_trailing_newline():
    assert render_jinja_source("text\n", Environment()) == "text\n"


def test_render_data_key_empty_mapping():
    # Empty mappings are not flattened by the
    # environment, so they are stored as
    # plain dictionaries.
    environment = Environment.from_dict({"name": "Mau", "selected": {}})

    result = render_jinja_source("text", environment, data_key="selected")

    assert result == "text"


@pytest.mark.parametrize(
    "data_key,type_name",
    [
        ("mau.changelog.versions", "list"),
        ("mau.changelog.latest", "str"),
        ("mau.changelog.versions_count", "int"),
        ("mau.changelog.empty", "NoneType"),
    ],
)
def test_render_data_key_not_a_mapping(data_key, type_name):
    environment = Environment.from_dict(
        {
            "changelog": {
                **MAU_ENVIRONMENT["mau"]["changelog"],
                "versions_count": 2,
                "empty": None,
            }
        },
        "mau",
    )
    context = generate_context(3, 0, 3, 20)

    with pytest.raises(MauException) as exc:
        render_jinja_source("text", environment, data_key=data_key, context=context)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == (
        f"Data key '{data_key}' must point to a mapping, found {type_name}."
    )
    assert exc.value.message.context == context


def test_render_missing_data_key():
    context = generate_context(3, 0, 3, 20)

    with pytest.raises(MauException) as exc:
        render_jinja_source(
            "text", Environment(), data_key="does.not.exist", context=context
        )

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Data key 'does.not.exist' not found in the Mau environment."
    )
    assert exc.value.message.context == context


def test_render_undefined_variable():
    source = dedent("""
    First line
    Second line
    {{ missing }}
    """)

    with pytest.raises(MauException) as exc:
        render_jinja_source(source, Environment(), source_filename="included.mau")

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Jinja rendering error: 'missing' is undefined"
    assert exc.value.message.context == Context(2, 0, 2, 0, "included.mau")


def test_render_undefined_attribute_inside_loop():
    environment = Environment.from_dict({"items": [{"id": "a"}]})

    source = dedent("""
    {% for item in items %}
    * {{ item.name }}
    {% endfor %}
    """)

    with pytest.raises(MauException) as exc:
        render_jinja_source(source, environment, source_filename="included.mau")

    assert exc.value.message.text.startswith("Jinja rendering error:")
    assert "name" in exc.value.message.text
    assert exc.value.message.context == Context(1, 0, 1, 0, "included.mau")


def test_render_syntax_error():
    source = dedent("""
    First line
    {% for x in %}
    {% endfor %}
    """)

    with pytest.raises(MauException) as exc:
        render_jinja_source(source, Environment(), source_filename="included.mau")

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text.startswith("Jinja syntax error:")
    assert exc.value.message.context == Context(1, 0, 1, 0, "included.mau")


def test_render_custom_jinja_options():
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
            "name": "Mau",
        },
        "mau",
    )

    # With custom delimiters, double curly braces
    # are left untouched for Mau.
    result = render_jinja_source("[[ mau.name ]] {{escaped}}", environment)

    assert result == "Mau {{escaped}}"


def test_render_custom_jinja_options_override_defaults():
    environment = Environment.from_dict(
        {"parser": {"jinja": {"options": {"trim_blocks": False}}}, "entries": ["a"]},
        "mau",
    )

    source = "{% for i in mau.entries %}\n* {{ i }}\n{% endfor %}\n"

    assert render_jinja_source(source, environment) == "\n* a\n\n"


def test_render_non_jinja_exception():
    # Jinja resolves `items` as the dictionary
    # method, which is not iterable. The resulting
    # TypeError must be reported as a Mau error.
    environment = Environment.from_dict({"config": {"items": ["a"]}})

    source = dedent("""
    First line
    {% for i in config.items %}{{ i }}{% endfor %}
    """)

    with pytest.raises(MauException) as exc:
        render_jinja_source(source, environment, source_filename="included.mau")

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text.startswith("Jinja rendering error:")
    assert "not iterable" in exc.value.message.text
    assert exc.value.message.context == Context(1, 0, 1, 0, "included.mau")
