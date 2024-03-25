import textwrap
from unittest.mock import patch

import pytest
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.footnotes import FootnoteNode, FootnotesEntryNode, FootnotesNode
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import ContainerNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.toc import TocNode
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
    parser.footnote_entries = []

    assert parser.nodes == [
        FootnotesNode(
            parser.footnote_entries,
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
    parser.footnote_mentions = {
        "note1": FootnoteNode(number=1),
        "note2": FootnoteNode(number=2),
    }
    parser.parse(parser.tokens)

    assert parser.nodes == []
    assert parser.footnote_mentions == {
        "note1": FootnoteNode(
            number=1,
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("This is a paragraph."),
                        ]
                    )
                ),
            ],
            reference_anchor="ref-footnote-1-XXYY",
            content_anchor="cnt-footnote-1-XXYY",
        ),
        "note2": FootnoteNode(
            number=2,
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("This is another paragraph."),
                        ]
                    )
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

    assert parser.footnote_mentions == {
        "note1": FootnoteNode(
            number=1,
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("This is the content of the footnote"),
                        ]
                    )
                ),
            ],
            reference_anchor="ref-footnote-1-XXYY",
            content_anchor="cnt-footnote-1-XXYY",
        )
    }
    assert parser.footnote_data == {
        "note1": {
            "content": [
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("This is the content of the footnote"),
                        ]
                    )
                )
            ],
        }
    }

    footnote_mention = parser.footnote_mentions["note1"]

    assert parser.footnotes == [footnote_mention.to_entry()]


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
            SentenceNode(
                [
                    TextNode("This is a paragraph with a footnote"),
                    FootnoteNode(
                        [
                            ParagraphNode(
                                SentenceNode(
                                    [
                                        TextNode("This is the content of the footnote"),
                                    ]
                                )
                            )
                        ],
                        number=1,
                        reference_anchor="ref-footnote-1-XXYY",
                        content_anchor="cnt-footnote-1-XXYY",
                    ),
                    TextNode("."),
                ]
            )
        ),
        FootnotesNode(
            [
                FootnotesEntryNode(
                    [
                        ParagraphNode(
                            SentenceNode(
                                [
                                    TextNode("This is the content of the footnote"),
                                ]
                            )
                        )
                    ],
                    number=1,
                    reference_anchor="ref-footnote-1-XXYY",
                    content_anchor="cnt-footnote-1-XXYY",
                ),
            ]
        ),
    ]

    assert parser.output == {
        "content": ContainerNode(content=parser.nodes),
        "footnotes": [
            FootnotesEntryNode(
                [
                    ParagraphNode(
                        SentenceNode(
                            [
                                TextNode("This is the content of the footnote"),
                            ]
                        )
                    )
                ],
                number=1,
                reference_anchor="ref-footnote-1-XXYY",
                content_anchor="cnt-footnote-1-XXYY",
            ),
        ],
        "references": {},
        "toc": TocNode(entries=[]),
        "custom_filters": {},
    }


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
