import textwrap
from unittest.mock import patch

from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import TextNode
from mau.nodes.page import ContainerNode
from mau.nodes.paragraph import ParagraphNode
from mau.nodes.references import ReferenceNode, ReferencesEntryNode, ReferencesNode
from mau.nodes.toc import TocNode
from mau.parsers.main_parser import MainParser
from mau.parsers.references import reference_anchor

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_command_references_parse_args():
    source = """
    [*subtype1, arg1, arg2, #tag1, key1=value1, key2=value2]
    ::references:content_type
    """

    parser = runner(source)

    assert parser.nodes == [
        ReferencesNode(
            content_type="content_type",
            entries=[],
            subtype="subtype1",
            args=["arg1", "arg2"],
            kwargs={"key1": "value1", "key2": "value2"},
            tags=["tag1"],
        ),
    ]


@patch("mau.parsers.references.hashlib.md5")
def test_default_reference_anchor_function(mock_md5):
    mock_md5().hexdigest.return_value = "XXYYXXYYZZZ"

    assert reference_anchor("Some Words 1234 56") == "XXYYXXYY"


def test_document_with_reference():
    source = """
    . Some title
    [*reference, content_type, value]
    ----
    This is a paragraph.
    ----
    """

    parser = runner(textwrap.dedent(source))

    assert parser.nodes == []
    assert parser.references_manager.data[("content_type", "value")] == [
        ParagraphNode(
            children=[
                TextNode("This is a paragraph."),
            ]
        ),
    ]


@patch("mau.parsers.references.reference_anchor")
def test_simple_reference(mock_reference_anchor):
    source = """
    This is a paragraph with a [reference](content_type, value)

    [*reference, content_type, value]
    ----
    This is a paragraph.
    ----
    """

    mock_reference_anchor.return_value = "XXYY"

    parser = runner(source)

    assert parser.output["references"] == {
        ("content_type", "value"): ReferencesEntryNode(
            "content_type",
            content=[
                ParagraphNode(
                    children=[
                        TextNode("This is a paragraph."),
                    ]
                ),
            ],
            number=1,
            reference_anchor="ref-content_type-1-XXYY",
            content_anchor="cnt-content_type-1-XXYY",
        ),
    }


@patch("mau.parsers.references.reference_anchor")
def test_reference_data_inside_block(mock_reference_anchor):
    source = """
    This is a paragraph with a [reference](content_type, value)

    [someblock]
    ====
    [*reference, content_type, value]
    ----
    This is a paragraph.
    ----
    ====
    """

    mock_reference_anchor.return_value = "XXYY"

    parser = runner(source)

    assert parser.output["references"] == {
        ("content_type", "value"): ReferencesEntryNode(
            "content_type",
            content=[
                ParagraphNode(
                    children=[
                        TextNode("This is a paragraph."),
                    ]
                ),
            ],
            number=1,
            reference_anchor="ref-content_type-1-XXYY",
            content_anchor="cnt-content_type-1-XXYY",
        ),
    }


@patch("mau.parsers.references.reference_anchor")
def test_reference_mention_and_data_inside_block(mock_reference_anchor):
    source = """
    [someblock]
    ====
    This is a paragraph with a [reference](content_type, value)

    [*reference, content_type, value]
    ----
    This is a paragraph.
    ----
    ====
    """

    mock_reference_anchor.return_value = "XXYY"

    parser = runner(source)

    assert parser.output["references"] == {
        ("content_type", "value"): ReferencesEntryNode(
            "content_type",
            content=[
                ParagraphNode(
                    children=[
                        TextNode("This is a paragraph."),
                    ]
                ),
            ],
            number=1,
            reference_anchor="ref-content_type-1-XXYY",
            content_anchor="cnt-content_type-1-XXYY",
        ),
    }


@patch("mau.parsers.references.reference_anchor")
def test_multiple_content_types(mock_reference_anchor):
    mock_reference_anchor.return_value = "XXYY"

    source = """
    [*reference, content_type1, name1]
    ----
    Content type 1, value 1
    ----

    [*reference, content_type1, name2]
    ----
    Content type 1, value 2
    ----

    [*reference, content_type2, name1]
    ----
    Content type 2, value 1
    ----

    This is a paragraph with references of different types:
    [reference](content_type1, name1), [reference](content_type1, name2), [reference](content_type2, name1)
    """

    parser = runner(source)

    assert parser.output["references"] == {
        ("content_type1", "name1"): ReferenceNode(
            "content_type1",
            content=[
                ParagraphNode(
                    children=[
                        TextNode("Content type 1, value 1"),
                    ]
                ),
            ],
            number=1,
            reference_anchor="ref-content_type1-1-XXYY",
            content_anchor="cnt-content_type1-1-XXYY",
        ).to_entry(),
        ("content_type1", "name2"): ReferenceNode(
            "content_type1",
            content=[
                ParagraphNode(
                    children=[
                        TextNode("Content type 1, value 2"),
                    ]
                ),
            ],
            number=2,
            reference_anchor="ref-content_type1-2-XXYY",
            content_anchor="cnt-content_type1-2-XXYY",
        ).to_entry(),
        ("content_type2", "name1"): ReferenceNode(
            "content_type2",
            content=[
                ParagraphNode(
                    children=[
                        TextNode("Content type 2, value 1"),
                    ]
                ),
            ],
            number=3,
            reference_anchor="ref-content_type2-3-XXYY",
            content_anchor="cnt-content_type2-3-XXYY",
        ).to_entry(),
    }


@patch("mau.parsers.references.reference_anchor")
def test_command_references_filter_content_type(mock_reference_anchor):
    mock_reference_anchor.return_value = "XXYY"

    source = """
    [*reference, content_type1, name1]
    ----
    Content type 1, value 1
    ----

    [*reference, content_type1, name2]
    ----
    Content type 1, value 2
    ----

    [*reference, content_type2, name1]
    ----
    Content type 2, value 1
    ----

    This is a paragraph with references of different types:
    [reference](content_type1, name1), [reference](content_type1, name2), [reference](content_type2, name1)

    ::references:content_type1
    """

    parser = runner(source)

    assert parser.nodes == [
        ParagraphNode(
            children=[
                TextNode("This is a paragraph with references of different types: "),
                ReferenceNode(
                    "content_type1",
                    content=[
                        ParagraphNode(children=[TextNode("Content type 1, value 1")]),
                    ],
                    number=1,
                    reference_anchor="ref-content_type1-1-XXYY",
                    content_anchor="cnt-content_type1-1-XXYY",
                ),
                TextNode(", "),
                ReferenceNode(
                    "content_type1",
                    content=[
                        ParagraphNode(children=[TextNode("Content type 1, value 2")]),
                    ],
                    number=2,
                    reference_anchor="ref-content_type1-2-XXYY",
                    content_anchor="cnt-content_type1-2-XXYY",
                ),
                TextNode(", "),
                ReferenceNode(
                    "content_type2",
                    content=[
                        ParagraphNode(children=[TextNode("Content type 2, value 1")]),
                    ],
                    number=3,
                    reference_anchor="ref-content_type2-3-XXYY",
                    content_anchor="cnt-content_type2-3-XXYY",
                ),
            ],
            args=[],
            kwargs={},
        ),
        ReferencesNode(
            content_type="content_type1",
            entries=[
                ReferencesEntryNode(
                    "content_type1",
                    content=[
                        ParagraphNode(children=[TextNode("Content type 1, value 1")]),
                    ],
                    number=1,
                    reference_anchor="ref-content_type1-1-XXYY",
                    content_anchor="cnt-content_type1-1-XXYY",
                ),
                ReferencesEntryNode(
                    "content_type1",
                    content=[
                        ParagraphNode(children=[TextNode("Content type 1, value 2")]),
                    ],
                    number=2,
                    reference_anchor="ref-content_type1-2-XXYY",
                    content_anchor="cnt-content_type1-2-XXYY",
                ),
            ],
            args=[],
            kwargs={},
            tags=[],
        ),
    ]


@patch("mau.parsers.references.reference_anchor")
def test_references_output(mock_reference_anchor):
    mock_reference_anchor.return_value = "XXYY"

    source = """
    [*reference, content_type1, name1]
    ----
    Content type 1, value 1
    ----

    This is a paragraph with a reference [reference](content_type1, name1).

    ::references:content_type1
    """

    parser = runner(source)

    assert parser.output == {
        "content": ContainerNode(
            children=[
                ParagraphNode(
                    children=[
                        TextNode("This is a paragraph with a reference "),
                        ReferenceNode(
                            "content_type1",
                            content=[
                                ParagraphNode(
                                    children=[TextNode("Content type 1, value 1")]
                                ),
                            ],
                            number=1,
                            reference_anchor="ref-content_type1-1-XXYY",
                            content_anchor="cnt-content_type1-1-XXYY",
                        ),
                        TextNode("."),
                    ],
                    args=[],
                    kwargs={},
                ),
                ReferencesNode(
                    content_type="content_type1",
                    entries=[
                        ReferencesEntryNode(
                            "content_type1",
                            content=[
                                ParagraphNode(
                                    children=[TextNode("Content type 1, value 1")]
                                ),
                            ],
                            number=1,
                            reference_anchor="ref-content_type1-1-XXYY",
                            content_anchor="cnt-content_type1-1-XXYY",
                        ),
                    ],
                    args=[],
                    kwargs={},
                    tags=[],
                ),
            ]
        ),
        "footnotes": [],
        "references": {
            ("content_type1", "name1"): ReferencesEntryNode(
                "content_type1",
                content=[
                    ParagraphNode(children=[TextNode("Content type 1, value 1")]),
                ],
                number=1,
                reference_anchor="ref-content_type1-1-XXYY",
                content_anchor="cnt-content_type1-1-XXYY",
            )
        },
        "toc": TocNode(),
        "custom_filters": {},
    }
