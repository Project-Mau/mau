from unittest.mock import call, mock_open, patch

import pytest

from mau.environment.environment import Environment
from mau.message import MauException, MauMessageType
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import NullMessageHandler, dedent
from mau.text_buffer import Context

FILE_MODE = {"parser": {"include_paths_strategy": "file"}}
CWD_MODE = {"parser": {"include_paths_strategy": "cwd"}}


def _parse(source, config=None, source_filename="book/main.mau"):
    # Parse the source as if it was stored
    # in the file `source_filename`.
    environment = Environment.from_dict(config or {}, "mau")

    return DocumentParser.lex_and_parse(
        dedent(source),
        NullMessageHandler(),
        environment,
        source_filename=source_filename,
    )


def _opened_paths(mocked_open):
    # The paths passed to `open`, in order.
    return [c.args[0] for c in mocked_open.call_args_list]


def _include_files(*texts):
    # Patch `open` so that each call returns
    # the next text in the given order.
    mocks = [mock_open(read_data=text).return_value for text in texts]

    return patch("builtins.open", side_effect=mocks)


def test_include_paths_strategy_default_is_cwd():
    source = """
    << mau:chapter.mau
    """

    with _include_files("Text.") as mocked_open:
        parser = _parse(source)

    assert parser.include_paths_strategy == "cwd"
    assert _opened_paths(mocked_open) == ["chapter.mau"]


def test_include_paths_strategy_cwd():
    source = """
    << mau:chapter.mau
    """

    with _include_files("Text.") as mocked_open:
        _parse(source, CWD_MODE)

    assert _opened_paths(mocked_open) == ["chapter.mau"]


def test_include_paths_strategy_file():
    source = """
    << mau:chapter.mau
    """

    with _include_files("Text.") as mocked_open:
        parser = _parse(source, FILE_MODE)

    assert mocked_open.call_args_list == [
        call("book/chapter.mau", "r", encoding="utf-8")
    ]

    include_node = parser.nodes[0]

    # The node keeps the URI as written.
    assert include_node.uri == "chapter.mau"

    # The included content comes from
    # the resolved path.
    paragraph_node = include_node.content[0]
    assert paragraph_node.info.context.source == "book/chapter.mau"

    # The include call records the resolved path.
    (include_call,) = parser.output.include_calls
    assert include_call.caller_uri == "book/main.mau"
    assert include_call.callee_uri == "book/chapter.mau"


def test_include_paths_strategy_file_nested():
    # Includes inside an included file are
    # relative to the included file.
    source = """
    << mau:parts/chapter.mau
    """

    CHAPTER_TEXT = dedent("""
    << mau:section.mau
    """)

    with _include_files(CHAPTER_TEXT, "Text.") as mocked_open:
        _parse(source, FILE_MODE)

    assert _opened_paths(mocked_open) == [
        "book/parts/chapter.mau",
        "book/parts/section.mau",
    ]


def test_include_paths_strategy_file_parent_directory():
    # The main file is in `pdf/` and includes
    # chapters stored in `src/`. A chapter includes
    # a file stored next to it in `src/`.
    source = """
    << mau:../src/98_Changelog.mau
    """

    CHAPTER_TEXT = dedent("""
    << mau:changelog.mau
    """)

    with _include_files(CHAPTER_TEXT, "Text.") as mocked_open:
        _parse(source, FILE_MODE, source_filename="book/pdf/book.mau")

    assert _opened_paths(mocked_open) == [
        "book/pdf/../src/98_Changelog.mau",
        "book/pdf/../src/changelog.mau",
    ]


def test_include_paths_strategy_file_absolute_path():
    source = """
    << mau:/absolute/path/chapter.mau
    """

    with _include_files("Text.") as mocked_open:
        _parse(source, FILE_MODE)

    assert _opened_paths(mocked_open) == ["/absolute/path/chapter.mau"]


def test_include_paths_strategy_file_without_source_uses_cwd():
    # Text that doesn't come from a file
    # falls back to the working directory.
    source = """
    << mau:chapter.mau
    """

    with _include_files("Text.") as mocked_open:
        _parse(source, FILE_MODE, source_filename=None)

    assert _opened_paths(mocked_open) == ["chapter.mau"]


def test_include_paths_strategy_file_raw():
    source = """
    << raw:code/example.txt
    """

    with _include_files("Raw text.") as mocked_open:
        parser = _parse(source, FILE_MODE)

    assert _opened_paths(mocked_open) == ["book/code/example.txt"]

    # The node keeps the URI as written.
    assert parser.nodes[0].uri == "code/example.txt"


def test_include_paths_strategy_file_without_environment():
    # The setting applies to the whole document,
    # even to included files that don't receive the
    # environment, and to the blocks they contain.
    source = """
    << mau:parts/chapter.mau, pass_environment=false
    """

    CHAPTER_TEXT = dedent("""
    << mau:section.mau

    ----
    << mau:other_section.mau
    ----
    """)

    with _include_files(CHAPTER_TEXT, "Text.", "Text.") as mocked_open:
        _parse(source, FILE_MODE)

    assert _opened_paths(mocked_open) == [
        "book/parts/chapter.mau",
        "book/parts/section.mau",
        "book/parts/other_section.mau",
    ]


def test_include_paths_strategy_file_missing_file():
    # The error shows the path that Mau tried to open.
    source = """
    << mau:does_not_exist.mau
    """

    with pytest.raises(MauException) as exc:
        _parse(source, FILE_MODE, source_filename="not/a/real/dir/main.mau")

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "File 'not/a/real/dir/does_not_exist.mau' cannot be read."
    )


def test_include_paths_strategy_file_self_inclusion():
    # With file-relative paths, including a file
    # with its own name is a self-inclusion.
    source = """
    << mau:main.mau
    """

    with pytest.raises(MauException) as exc:
        _parse(source, FILE_MODE)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text.startswith("To avoid recursion")


def test_include_paths_strategy_cwd_same_name_is_another_file():
    # With paths relative to the working directory,
    # `main.mau` is not the file `book/main.mau`.
    source = """
    << mau:main.mau
    """

    with _include_files("Text.") as mocked_open:
        _parse(source, CWD_MODE)

    assert _opened_paths(mocked_open) == ["main.mau"]


def test_include_paths_strategy_file_jinja_error_points_to_resolved_path():
    source = """
    << mau:chapter.mau, preprocess=jinja
    """

    with pytest.raises(MauException) as exc, _include_files("{{ missing }}"):
        _parse(source, FILE_MODE)

    assert exc.value.message.text == "Jinja rendering error: 'missing' is undefined"
    assert exc.value.message.context == Context(0, 0, 0, 0, "book/chapter.mau")


def test_include_paths_strategy_invalid_value():
    with pytest.raises(MauException) as exc:
        _parse("Text.", {"parser": {"include_paths_strategy": "somewhere"}})

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == (
        "Configuration value 'mau.parser.include_paths_strategy' must be one of "
        "['cwd', 'file'], found 'somewhere'."
    )
