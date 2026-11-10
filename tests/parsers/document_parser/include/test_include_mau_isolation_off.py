from unittest.mock import mock_open, patch

import pytest

from mau.lexers.document_lexer import DocumentLexer
from mau.message import MauException, MauMessageType
from mau.parsers.document_parser import DocumentParser
from mau.test_helpers import dedent, parser_runner_factory

runner = parser_runner_factory(DocumentLexer, DocumentParser)


def _run_with_file(source, included_text):
    # Run the parser on the source, providing
    # the given text as the included file.
    with patch("builtins.open", mock_open(read_data=included_text)):
        return runner(source)


def test_include_mau_is_isolated_by_default():
    source = """
    << toc

    << mau:/path/to/it
    """

    MAU_TEXT = dedent("""
    = Included header
    """)

    parser = _run_with_file(source, MAU_TEXT)

    assert parser.toc_manager.headers == []
    assert parser.nodes[0].plain_entries == []


def test_include_mau_isolation_off_adds_headers_to_global_toc():
    source = """
    << toc

    = Main header

    << mau:/path/to/it, isolate=false
    """

    MAU_TEXT = dedent("""
    == Included header
    """)

    parser = _run_with_file(source, MAU_TEXT)

    assert [header.level for header in parser.toc_manager.headers] == [1, 2]

    toc_node = parser.nodes[0]

    assert len(toc_node.plain_entries) == 2

    # The included header is nested
    # under the main header.
    assert len(toc_node.nested_entries) == 1
    assert len(toc_node.nested_entries[0].entries) == 1

    # The included header has been given
    # an internal ID by the includer.
    included_header = parser.toc_manager.headers[1]
    assert included_header.internal_id is not None


def test_include_mau_isolation_off_toc_in_included_file():
    # A ToC in a non-isolated included file
    # lists the headers of the whole document.
    source = """
    = Main header

    << mau:/path/to/it, isolate=false
    """

    MAU_TEXT = dedent("""
    << toc

    == Included header
    """)

    parser = _run_with_file(source, MAU_TEXT)

    toc_node = parser.nodes[1].content[0]

    assert len(toc_node.plain_entries) == 2


def test_include_mau_isolation_off_argument_is_consumed():
    source = """
    << mau:/path/to/it, isolate=false
    """

    parser = _run_with_file(source, "Some text.")

    assert parser.nodes[0].arguments.named_args == {}


def test_include_mau_isolation_off_footnote_body_in_included_file():
    source = """
    Some text with a [footnote](note).

    << mau:/path/to/it, isolate=false
    """

    MAU_TEXT = dedent("""
    [footnote=note]
    ----
    The footnote body.
    ----
    """)

    parser = _run_with_file(source, MAU_TEXT)

    assert list(parser.footnotes_manager.footnotes_dict) == ["note"]

    (macro,) = parser.footnotes_manager.footnote_macros
    assert macro.footnote is parser.footnotes_manager.footnotes_dict["note"]


def test_include_mau_isolated_footnote_body_in_included_file():
    source = """
    Some text with a [footnote](note).

    << mau:/path/to/it
    """

    MAU_TEXT = dedent("""
    [footnote=note]
    ----
    The footnote body.
    ----
    """)

    with pytest.raises(MauException) as exc:
        _run_with_file(source, MAU_TEXT)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Footnote 'note' has not been defined."


def test_include_mau_isolation_off_footnote_mention_in_included_file():
    # The included file can mention a footnote
    # whose body is in the includer. This requires
    # the included file not to process its own
    # footnotes before they are merged.
    source = """
    << mau:/path/to/it, isolate=false

    [footnote=note]
    ----
    The footnote body.
    ----
    """

    MAU_TEXT = dedent("""
    Some text with a [footnote](note).
    """)

    parser = _run_with_file(source, MAU_TEXT)

    (macro,) = parser.footnotes_manager.footnote_macros
    assert macro.footnote is parser.footnotes_manager.footnotes_dict["note"]


def test_include_mau_isolation_off_footnotes_are_numbered_globally():
    source = """
    Main text with a [footnote](note1).

    [footnote=note1]
    ----
    The first footnote.
    ----

    << mau:/path/to/it, isolate=false
    """

    MAU_TEXT = dedent("""
    Included text with a [footnote](note2).

    [footnote=note2]
    ----
    The second footnote.
    ----
    """)

    parser = _run_with_file(source, MAU_TEXT)

    footnotes = parser.footnotes_manager.footnotes_dict

    assert [(name, f.public_id) for name, f in footnotes.items()] == [
        ("note1", "1"),
        ("note2", "2"),
    ]


def test_include_mau_isolation_off_header_link_to_included_header():
    source = """
    See [header](intro).

    << mau:/path/to/it, isolate=false
    """

    MAU_TEXT = dedent("""
    [name=intro]
    = Introduction
    """)

    parser = _run_with_file(source, MAU_TEXT)

    (macro,) = parser.header_links_manager.macros
    assert macro.header is parser.header_links_manager.headers["intro"]
    assert macro.header.internal_id is not None


def test_include_mau_isolation_off_header_link_from_included_file():
    # The included file can link a header of the
    # includer. This requires the included file not
    # to process its own header links before they
    # are merged.
    source = """
    [name=intro]
    = Introduction

    << mau:/path/to/it, isolate=false
    """

    MAU_TEXT = dedent("""
    See [header](intro).
    """)

    parser = _run_with_file(source, MAU_TEXT)

    (macro,) = parser.header_links_manager.macros
    assert macro.header is parser.header_links_manager.headers["intro"]


def test_include_mau_isolated_header_link_from_included_file():
    source = """
    [name=intro]
    = Introduction

    << mau:/path/to/it
    """

    MAU_TEXT = dedent("""
    See [header](intro).
    """)

    with pytest.raises(MauException) as exc:
        _run_with_file(source, MAU_TEXT)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Cannot find header with id intro"


def test_include_mau_isolation_off_duplicate_header_name():
    source = """
    [name=intro]
    = Introduction

    << mau:/path/to/it, isolate=false
    """

    MAU_TEXT = dedent("""
    [name=intro]
    = Another introduction
    """)

    with pytest.raises(MauException) as exc:
        _run_with_file(source, MAU_TEXT)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "Duplicate header id detected: intro"


def test_include_mau_isolation_off_is_transitive():
    # Headers of a non-isolated file included
    # by a non-isolated file reach the main document.
    source = """
    = Main header

    << mau:/path/to/it, isolate=false
    """

    MAU_TEXT_1 = dedent("""
    == First included header

    << mau:/another/path, isolate=false
    """)

    MAU_TEXT_2 = dedent("""
    === Second included header
    """)

    m1 = mock_open(read_data=MAU_TEXT_1)
    m2 = mock_open(read_data=MAU_TEXT_2)

    with patch("builtins.open", side_effect=[m1.return_value, m2.return_value]):
        parser = runner(source)

    assert [header.level for header in parser.toc_manager.headers] == [1, 2, 3]


def test_include_mau_isolation_off_inside_isolated_file():
    # Headers of a non-isolated file included
    # by an isolated file stop at the isolated file.
    source = """
    = Main header

    << mau:/path/to/it
    """

    MAU_TEXT_1 = dedent("""
    == First included header

    << mau:/another/path, isolate=false
    """)

    MAU_TEXT_2 = dedent("""
    === Second included header
    """)

    m1 = mock_open(read_data=MAU_TEXT_1)
    m2 = mock_open(read_data=MAU_TEXT_2)

    with patch("builtins.open", side_effect=[m1.return_value, m2.return_value]):
        parser = runner(source)

    assert [header.level for header in parser.toc_manager.headers] == [1]
