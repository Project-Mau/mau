import textwrap
from unittest.mock import patch

import pytest
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockNode
from mau.nodes.footnotes import FootnoteNode, FootnotesEntryNode, FootnotesNode
from mau.nodes.inline import TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.parsers.footnotes import footnote_anchor
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_command_footnotes():
    source = """
    [*subtype1, arg1, arg2, #tag1, key1=value1, key2=value2]
    ::footnotes:
    """

    parser = runner(source)
    parser.footnotes_manager.footnotes = []

    assert parser.nodes == [
        FootnotesNode(
            children=parser.footnotes_manager.footnotes,
            subtype="subtype1",
            args=["arg1", "arg2"],
            kwargs={"key1": "value1", "key2": "value2"},
            tags=["tag1"],
        ),
    ]


@patch("mau.parsers.footnotes.hashlib.md5")
def test_default_footnote_anchor_function(mock_md5):
    mock_md5().hexdigest.return_value = "XXYYXXYYZZZ"

    assert footnote_anchor("Some Words 1234 56") == "XXYYXXYY"


def test_footnote_empty_block():
    source = """
    [*footnote, note1]
    ----
    ----
    """

    parser = runner(textwrap.dedent(source))
    parser.footnotes = {
        "note1": FootnoteNode(number=1),
    }

    assert parser.nodes == []


@patch("mau.parsers.footnotes.footnote_anchor")
def test_footnote_content(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    [*footnote, note2]
    ----
    This is another paragraph.
    ----

    [*footnote, note1]
    ----
    This is a paragraph.
    ----
    """

    parser = runner(textwrap.dedent(source))
    parser.footnotes_manager.mentions = {
        "note1": FootnoteNode(number=1),
        "note2": FootnoteNode(number=2),
    }
    parser.finalise()

    assert parser.nodes == []
    assert parser.footnotes_manager.mentions == {
        "note1": FootnoteNode(
            number=1,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is a paragraph."),
                    ]
                )
            ],
            reference_anchor="ref-footnote-1-XXYY",
            content_anchor="cnt-footnote-1-XXYY",
        ),
        "note2": FootnoteNode(
            number=2,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is another paragraph."),
                    ]
                ),
            ],
            reference_anchor="ref-footnote-2-XXYY",
            content_anchor="cnt-footnote-2-XXYY",
        ),
    }


@patch("mau.parsers.footnotes.footnote_anchor")
def test_footnote_mention_and_content(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    This is a paragraph with a footnote[footnote](note1).
    
    [*footnote, note1]
    ----
    This is the content of the footnote
    ----
    """

    parser = runner(textwrap.dedent(source))

    assert parser.footnotes_manager.mentions == {
        "note1": FootnoteNode(
            number=1,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is the content of the footnote"),
                    ]
                ),
            ],
            reference_anchor="ref-footnote-1-XXYY",
            content_anchor="cnt-footnote-1-XXYY",
        )
    }
    assert parser.footnotes_manager.data == {
        "note1": [
            ParagraphNode(
                children=[
                    TextNode("This is the content of the footnote"),
                ]
            )
        ],
    }


@patch("mau.parsers.footnotes.footnote_anchor")
def test_footnotes_output(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    This is a paragraph with a footnote[footnote](note1).
    
    [*footnote, note1]
    ----
    This is the content of the footnote
    ----

    ::footnotes:
    """

    parser = runner(textwrap.dedent(source))

    assert parser.nodes == [
        ParagraphNode(
            children=[
                TextNode("This is a paragraph with a footnote"),
                FootnoteNode(
                    children=[
                        ParagraphNode(
                            children=[
                                TextNode("This is the content of the footnote"),
                            ]
                        )
                    ],
                    number=1,
                    reference_anchor="ref-footnote-1-XXYY",
                    content_anchor="cnt-footnote-1-XXYY",
                ),
                TextNode("."),
            ]
        ),
        FootnotesNode(
            children=[
                FootnotesEntryNode(
                    children=[
                        ParagraphNode(
                            children=[
                                TextNode("This is the content of the footnote"),
                            ]
                        )
                    ],
                    number=1,
                    reference_anchor="ref-footnote-1-XXYY",
                    content_anchor="cnt-footnote-1-XXYY",
                ),
            ]
        ),
    ]


@patch("mau.parsers.footnotes.footnote_anchor")
def test_footnotes_output_in_block(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    ++++
    This is a paragraph with a footnote[footnote](note1).
    
    [*footnote, note1]
    ----
    This is the content of the footnote
    ----

    ::footnotes:
    ++++
    """

    parser = runner(textwrap.dedent(source))

    assert parser.nodes == [
        BlockNode(
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is a paragraph with a footnote"),
                        FootnoteNode(
                            children=[
                                ParagraphNode(
                                    children=[
                                        TextNode("This is the content of the footnote"),
                                    ]
                                )
                            ],
                            number=1,
                            reference_anchor="ref-footnote-1-XXYY",
                            content_anchor="cnt-footnote-1-XXYY",
                        ),
                        TextNode("."),
                    ]
                ),
                FootnotesNode(
                    children=[
                        FootnotesEntryNode(
                            children=[
                                ParagraphNode(
                                    children=[
                                        TextNode("This is the content of the footnote"),
                                    ]
                                )
                            ],
                            number=1,
                            reference_anchor="ref-footnote-1-XXYY",
                            content_anchor="cnt-footnote-1-XXYY",
                        ),
                    ]
                ),
            ],
            preprocessor="none",
        )
    ]


def test_footnote_duplication():
    source = """
    [*footnote, note1]
    ----
    This is the content of the footnote
    ----

    This is a paragraph with a footnote[footnote](note1).

    This is a paragraph with the same footnote[footnote](note1).
    """

    with pytest.raises(MauErrorException):
        runner(textwrap.dedent(source))


@patch("mau.parsers.footnotes.footnote_anchor")
def test_footnote_data_and_mention_in_block(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    ====
    This is a paragraph with a footnote[footnote](note1).

    [*footnote, note1]
    ----
    This is the content of the footnote
    ----
    ====
    """

    parser = runner(textwrap.dedent(source))

    assert parser.footnotes_manager.mentions == {
        "note1": FootnoteNode(
            number=1,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is the content of the footnote"),
                    ]
                ),
            ],
            reference_anchor="ref-footnote-1-XXYY",
            content_anchor="cnt-footnote-1-XXYY",
        )
    }
    assert parser.footnotes_manager.data == {
        "note1": [
            ParagraphNode(
                children=[
                    TextNode("This is the content of the footnote"),
                ]
            )
        ],
    }


@patch("mau.parsers.footnotes.footnote_anchor")
def test_footnote_data_in_block(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    This is a paragraph with a footnote[footnote](note1).

    ====
    [*footnote, note1]
    ----
    This is the content of the footnote
    ----
    ====
    """

    parser = runner(textwrap.dedent(source))

    assert parser.footnotes_manager.mentions == {
        "note1": FootnoteNode(
            number=1,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is the content of the footnote"),
                    ]
                ),
            ],
            reference_anchor="ref-footnote-1-XXYY",
            content_anchor="cnt-footnote-1-XXYY",
        )
    }
    assert parser.footnotes_manager.data == {
        "note1": [
            ParagraphNode(
                children=[
                    TextNode("This is the content of the footnote"),
                ]
            )
        ],
    }


@patch("mau.parsers.footnotes.footnote_anchor")
def test_footnote_mention_in_block(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    ====
    This is a paragraph with a footnote[footnote](note1).
    ====

    [*footnote, note1]
    ----
    This is the content of the footnote
    ----
    """

    parser = runner(textwrap.dedent(source))

    assert parser.footnotes_manager.mentions == {
        "note1": FootnoteNode(
            number=1,
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is the content of the footnote"),
                    ]
                ),
            ],
            reference_anchor="ref-footnote-1-XXYY",
            content_anchor="cnt-footnote-1-XXYY",
        )
    }
    assert parser.footnotes_manager.data == {
        "note1": [
            ParagraphNode(
                children=[
                    TextNode("This is the content of the footnote"),
                ]
            )
        ],
    }


# If footnotes are not assigned correctly,
# the following test will fail as the parent of
# both footnotes will be the second FootnotesNode
@patch("mau.parsers.footnotes.footnote_anchor")
def test_footnotes_parent(mock_footnote_anchor):
    mock_footnote_anchor.return_value = "XXYY"

    source = """
    Footnote [footnote](note1).

    [*footnote, note1]
    ----
    ----

    ::footnotes:

    [#tag1]
    ::footnotes:
    """

    parser = runner(textwrap.dedent(source))

    first_footnotes = parser.nodes[1]
    second_footnotes = parser.nodes[2]

    first_footnotes_footnote = first_footnotes.children[0]
    second_footnotes_footnote = second_footnotes.children[0]

    assert first_footnotes_footnote.parent == first_footnotes
    assert second_footnotes_footnote.parent == second_footnotes
