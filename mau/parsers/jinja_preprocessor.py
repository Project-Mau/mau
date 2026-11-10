from __future__ import annotations

from types import TracebackType

import jinja2

from mau.environment.environment import Environment
from mau.parsers.base_parser import create_parser_exception
from mau.text_buffer import Context

# The environment key that contains user-defined
# options for the Jinja environment used to
# preprocess Mau sources, e.g.
#
# mau:
#   parser:
#     jinja:
#       options:
#         variable_start_string: "[["
#         variable_end_string: "]]"
JINJA_OPTIONS_KEY = "mau.parser.jinja.options"

# Default options of the Jinja environment.
#
# Mau is line-oriented and a blank line has
# a meaning (it closes lists and paragraphs),
# so block tags like {% for %} must not leave
# empty lines or indentation behind them.
#
# Undefined variables raise an error instead
# of silently rendering as empty strings.
DEFAULT_JINJA_OPTIONS = {
    "undefined": jinja2.StrictUndefined,
    "trim_blocks": True,
    "lstrip_blocks": True,
    "keep_trailing_newline": True,
}

# Jinja uses this filename for templates
# created from a string. It shows up in the
# frames of the tracebacks of rendering errors.
JINJA_STRING_TEMPLATE_FILENAME = "<template>"

# A sentinel that tells apart a missing
# key from a key whose value is None.
_MISSING = object()


# Merge the default options with those
# provided by the user in the environment.
def _get_jinja_options(environment: Environment) -> dict:
    # A dictionary of the default Jinja options.
    options = dict(DEFAULT_JINJA_OPTIONS)

    # The Jinja options defined in
    # the environment.
    user_options = environment.get(JINJA_OPTIONS_KEY)

    # If there are options, the environment
    # returns them as an Environment object,
    # otherwise as an empty dictionary.
    # Let's convert everything into a dictionary.
    if isinstance(user_options, Environment):
        user_options = user_options.asdict()

    # Merge the two dictionaries.
    if user_options:
        options.update(user_options)

    return options


# Return the part of the Mau environment
# used as template data in a dictionary
# form. If no `data_key` is provided,
# the whole environment is returned.
# If `data_key` is provided, only the
# mapping stored under that key is
# returned, and its keys become the
# top-level template variables.
def _jinja_template_data(
    environment: Environment, data_key: str | None, context: Context | None
) -> dict:
    # If no data key has been requested
    # the template receives the whole
    # environment as a nested dictionary.
    if data_key is None:
        return environment.asdict()

    value = environment.get(data_key, _MISSING)

    if value is _MISSING:
        raise create_parser_exception(
            f"Data key '{data_key}' not found in the Mau environment.",
            context=context,
        )

    # Non-empty mappings are namespaces,
    # so the environment returns them as
    # Environment objects. Convert them
    # into nested dictionaries.
    # Empty mappings are stored as they are,
    # so they are already dictionaries.
    if isinstance(value, Environment):
        value = value.asdict()

    # Jinja needs a mapping as template data,
    # so any other value (list, string,
    # number, date, None) is an error.
    if not isinstance(value, dict):
        raise create_parser_exception(
            (
                f"Data key '{data_key}' must point to a mapping, "
                f"found {type(value).__name__}."
            ),
            context=context,
        )

    return value


# Jinja rewrites the traceback of rendering
# errors so that it contains frames that point
# to the template source. Find the last of them
# and return its line number (1-based).
def _find_template_line(traceback: TracebackType | None) -> int | None:
    line = None

    while traceback is not None:
        if traceback.tb_frame.f_code.co_filename == JINJA_STRING_TEMPLATE_FILENAME:
            line = traceback.tb_lineno

        traceback = traceback.tb_next

    return line


# Build the context of an error found in the
# template. Jinja lines are 1-based while Mau
# lines are 0-based internally. When the line
# is unknown the context points to the
# beginning of the file.
def _jinja_template_context(line: int | None, source_filename: str | None) -> Context:
    mau_line = line - 1 if line else 0

    return Context(mau_line, 0, mau_line, 0, source_filename)


def render_jinja_source(
    text: str,
    environment: Environment,
    source_filename: str | None = None,
    data_key: str | None = None,
    context: Context | None = None,
) -> str:
    """
    Render a Mau source text as a Jinja template.

    The template receives the given environment as a
    nested dictionary. If `data_key` is given, the template
    receives only the mapping stored under that key, and
    the rest of the environment is not available.

    `source_filename` is the name of the file that
    contains the template, and it's used to report
    errors found in the template. `context` is the
    context of the instruction that requested the
    rendering, used to report errors related to the
    instruction itself, like a missing or invalid
    data key.
    """

    # Create the Jinja environment.
    jinja_environment = jinja2.Environment(**_get_jinja_options(environment))

    # Compile the text from the Mau
    # file as a Jinja template.
    try:
        template = jinja_environment.from_string(text)
    except jinja2.TemplateSyntaxError as exc:
        raise create_parser_exception(
            f"Jinja syntax error: {exc.message}",
            context=_jinja_template_context(exc.lineno, source_filename),
        ) from exc

    # Build the template data from
    # the Mau environment.
    template_data = _jinja_template_data(environment, data_key, context)

    # Render the template.
    # Templates run user code on user data, so
    # any exception (e.g. a TypeError raised
    # iterating a non-iterable value) is
    # reported as a Mau error that points
    # to the template line.
    try:
        return template.render(**template_data)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        raise create_parser_exception(
            f"Jinja rendering error: {exc}",
            context=_jinja_template_context(
                _find_template_line(exc.__traceback__), source_filename
            ),
        ) from exc
