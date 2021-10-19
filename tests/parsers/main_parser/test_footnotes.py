import pytest

from unittest.mock import patch

from mau.parsers.base_parser import ParserError
from mau.parsers.main_parser import MainParser

from tests.helpers import listasdict, init_parser_factory, parser_test_factory, dedent

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


@patch("mau.parsers.main_parser.header_anchor")
@patch("mau.parsers.text_parser.footnote_anchors")
def test_macro_footnote(footnote_anchors_mock, header_anchor_mock):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")
    header_anchor_mock.return_value = "HXXXXXX"

    source = """
    Some text[footnote](just a note)
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "Some text",
                    },
                    {
                        "refanchor": "refXYZ",
                        "defanchor": "defXYZ",
                        "number": 1,
                        "type": "footnote_ref",
                        "content": [
                            {
                                "type": "sentence",
                                "content": [
                                    {"type": "text", "value": "just a note"},
                                ],
                            }
                        ],
                    },
                ],
            },
        },
    ]

    p = _test(source, expected)

    assert p.footnotes.asdict() == {
        "type": "footnotes",
        "entries": [
            {
                "type": "footnote_def",
                "refanchor": "refXYZ",
                "defanchor": "defXYZ",
                "number": 1,
                "content": [
                    {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "just a note"},
                        ],
                    }
                ],
            }
        ],
    }


@patch("mau.parsers.text_parser.footnote_anchors")
def test_macro_footnote_inside_admonition(footnote_anchors_mock):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")

    p = init_parser(
        dedent(
            """
            Some text[footnote](note number 1)

            [admonition, someclass, someicon, somelabel]
            ----
            Some text[footnote](note number 2)
            ----
            """
        )
    )
    p.parse()

    assert p.footnotes.asdict() == {
        "type": "footnotes",
        "entries": [
            {
                "type": "footnote_def",
                "refanchor": "refXYZ",
                "defanchor": "defXYZ",
                "number": 1,
                "content": [
                    {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "note number 1"},
                        ],
                    }
                ],
            },
            {
                "type": "footnote_def",
                "refanchor": "refXYZ",
                "defanchor": "defXYZ",
                "number": 1,
                "content": [
                    {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "note number 2"},
                        ],
                    }
                ],
            },
        ],
    }


@patch("mau.parsers.main_parser.header_anchor")
@patch("mau.parsers.text_parser.footnote_anchors")
def test_macro_footnote_with_commas(footnote_anchors_mock, header_anchor_mock):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")
    header_anchor_mock.return_value = "HXXXXXX"

    source = """
    Some text[footnote](just a note, with commas)
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "Some text",
                    },
                    {
                        "refanchor": "refXYZ",
                        "defanchor": "defXYZ",
                        "number": 1,
                        "type": "footnote_ref",
                        "content": [
                            {
                                "type": "sentence",
                                "content": [
                                    {"type": "text", "value": "just a note"},
                                ],
                            }
                        ],
                    },
                ],
            },
        },
    ]

    with pytest.raises(ParserError):
        p = _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
@patch("mau.parsers.text_parser.footnote_anchors")
def test_macro_footnote_with_quotes_and_commas(
    footnote_anchors_mock, header_anchor_mock
):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")
    header_anchor_mock.return_value = "HXXXXXX"

    source = """
    Some text[footnote]("just a note, with commas")
    """

    expected = [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "Some text",
                    },
                    {
                        "refanchor": "refXYZ",
                        "defanchor": "defXYZ",
                        "number": 1,
                        "type": "footnote_ref",
                        "content": [
                            {
                                "type": "sentence",
                                "content": [
                                    {
                                        "type": "text",
                                        "value": "just a note, with commas",
                                    },
                                ],
                            }
                        ],
                    },
                ],
            },
        },
    ]

    p = _test(source, expected)

    assert p.footnotes.asdict() == {
        "type": "footnotes",
        "entries": [
            {
                "type": "footnote_def",
                "refanchor": "refXYZ",
                "defanchor": "defXYZ",
                "number": 1,
                "content": [
                    {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "just a note, with commas"},
                        ],
                    }
                ],
            }
        ],
    }
