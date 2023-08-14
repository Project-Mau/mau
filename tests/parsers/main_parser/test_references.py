import textwrap
from unittest.mock import patch

from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import SentenceNode, TextNode
from mau.nodes.page import ParagraphNode
from mau.nodes.references import (
    CommandReferencesNode,
    ReferenceNode,
    ReferencesEntryNode,
)
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


@patch("mau.parsers.text_parser.ReferenceNode")
def test_parse_paragraph_with_reference(mock_reference_node):
    source = """
    This is a paragraph with a [reference](content_type, value)
    """

    parser = runner(source)
    reference_node = mock_reference_node()

    assert parser.nodes == [
        ParagraphNode(
            SentenceNode([TextNode("This is a paragraph with a "), reference_node]),
            args=[],
            kwargs={},
        )
    ]
    assert parser.reference_mentions == {("content_type", "value"): reference_node}
    assert parser.reference_data == {}


def test_parse_document_with_reference():
    source = """
    . Some title
    [reference, content_type, value]
    ----
    This is a paragraph.
    ----
    """

    parser = init_parser(textwrap.dedent(source))
    parser.parse()

    assert parser.nodes == []
    assert parser.reference_data[("content_type", "value")] == {
        "content": [
            ParagraphNode(
                SentenceNode(
                    [
                        TextNode("This is a paragraph."),
                    ]
                )
            ),
        ],
        "title": SentenceNode(
            [
                TextNode("Some title"),
            ]
        ),
    }


@patch("mau.parsers.main_parser.reference_anchor")
def test_parse_reference(mock_reference_anchor):
    source = """
    This is a paragraph with a [reference](content_type, value)

    [reference, content_type, value]
    ----
    This is a paragraph.
    ----
    """

    mock_reference_anchor.return_value = "XXYY"

    parser = runner(source)
    parser.process_references()

    assert parser.references == {
        ("content_type", "value"): ReferenceNode(
            "content_type",
            "value",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("This is a paragraph."),
                        ]
                    )
                ),
            ],
            number=1,
            reference_anchor="ref-content_type-1-XXYY",
            content_anchor="cnt-content_type-1-XXYY",
        ),
    }


@patch("mau.parsers.main_parser.reference_anchor")
def test_parse_stored_content_multiple_content(mock_reference_anchor):
    mock_reference_anchor.return_value = "XXYY"

    source = """
    [reference, content_type1, value1]
    ----
    Content type 1, value 1
    ----

    [reference, content_type1, value2]
    ----
    Content type 1, value 2
    ----

    [reference, content_type2, value1]
    ----
    Content type 2, value 1
    ----

    This is a paragraph with references of different types:
    [reference](content_type1, value1), [reference](content_type1, value2), [reference](content_type2, value1)
    """

    parser = runner(source)
    parser.process_references()

    assert parser.references == {
        ("content_type1", "value1"): ReferenceNode(
            "content_type1",
            "value1",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("Content type 1, value 1"),
                        ]
                    )
                ),
            ],
            number=1,
            reference_anchor="ref-content_type1-1-XXYY",
            content_anchor="cnt-content_type1-1-XXYY",
        ),
        ("content_type1", "value2"): ReferenceNode(
            "content_type1",
            "value2",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("Content type 1, value 2"),
                        ]
                    )
                ),
            ],
            number=2,
            reference_anchor="ref-content_type1-2-XXYY",
            content_anchor="cnt-content_type1-2-XXYY",
        ),
        ("content_type2", "value1"): ReferenceNode(
            "content_type2",
            "value1",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("Content type 2, value 1"),
                        ]
                    )
                ),
            ],
            number=1,
            reference_anchor="ref-content_type2-1-XXYY",
            content_anchor="cnt-content_type2-1-XXYY",
        ),
    }

    assert parser.reference_entries == {
        ("content_type1", "value1"): ReferencesEntryNode(
            "content_type1",
            "value1",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("Content type 1, value 1"),
                        ]
                    )
                ),
            ],
            number=1,
            reference_anchor="ref-content_type1-1-XXYY",
            content_anchor="cnt-content_type1-1-XXYY",
        ),
        ("content_type1", "value2"): ReferencesEntryNode(
            "content_type1",
            "value2",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("Content type 1, value 2"),
                        ]
                    )
                ),
            ],
            number=2,
            reference_anchor="ref-content_type1-2-XXYY",
            content_anchor="cnt-content_type1-2-XXYY",
        ),
        ("content_type2", "value1"): ReferencesEntryNode(
            "content_type2",
            "value1",
            content=[
                ParagraphNode(
                    SentenceNode(
                        [
                            TextNode("Content type 2, value 1"),
                        ]
                    )
                ),
            ],
            number=1,
            reference_anchor="ref-content_type2-1-XXYY",
            content_anchor="cnt-content_type2-1-XXYY",
        ),
    }


def test_command_references_parse_args():
    source = "::references:content_type, category, value, arg1, #tag1, name1=value1, name2=value2"

    parser = init_parser(source)
    parser.parse()

    assert parser.nodes == [
        CommandReferencesNode(
            content_type="content_type",
            category="category",
            name="value",
            entries={},
            args=["arg1"],
            kwargs={"name1": "value1", "name2": "value2"},
            tags=["tag1"],
        ),
    ]


@patch("mau.parsers.main_parser.reference_anchor")
def test_command_references_only_content_type(mock_reference_anchor):
    mock_reference_anchor.return_value = "XXYY"

    source = """
    [reference, content_type1, value1]
    ----
    Content type 1, value 1
    ----

    [reference, content_type1, value2]
    ----
    Content type 1, value 2
    ----

    [reference, content_type2, value1]
    ----
    Content type 2, value 1
    ----

    This is a paragraph with references of different types:
    [reference](content_type1, value1), [reference](content_type1, value2), [reference](content_type2, value1)

    ::references:content_type1
    """

    parser = runner(source)
    parser.parse()
    parser.process_references()

    assert parser.nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    TextNode(
                        "This is a paragraph with references of different types: "
                    ),
                    ReferenceNode(
                        "content_type1",
                        "value1",
                        content=[
                            ParagraphNode(
                                SentenceNode([TextNode("Content type 1, value 1")])
                            ),
                        ],
                        number=1,
                        reference_anchor="ref-content_type1-1-XXYY",
                        content_anchor="cnt-content_type1-1-XXYY",
                    ),
                    TextNode(", "),
                    ReferenceNode(
                        "content_type1",
                        "value2",
                        content=[
                            ParagraphNode(
                                SentenceNode([TextNode("Content type 1, value 2")])
                            ),
                        ],
                        number=2,
                        reference_anchor="ref-content_type1-2-XXYY",
                        content_anchor="cnt-content_type1-2-XXYY",
                    ),
                    TextNode(", "),
                    ReferenceNode(
                        "content_type2",
                        "value1",
                        content=[
                            ParagraphNode(
                                SentenceNode([TextNode("Content type 2, value 1")])
                            ),
                        ],
                        number=1,
                        reference_anchor="ref-content_type2-1-XXYY",
                        content_anchor="cnt-content_type2-1-XXYY",
                    ),
                ]
            ),
            args=[],
            kwargs={},
        ),
        CommandReferencesNode(
            content_type="content_type1",
            entries=parser.reference_entries,
            args=[],
            kwargs={},
            tags=[],
        ),
    ]
