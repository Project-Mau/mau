from unittest.mock import patch

from mau.parsers import nodes
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_test_factory

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_default_header_anchor_function():
    source = """
    = Some Words 1234 56
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Some Words 1234 56",
            "level": 1,
            "anchor": "some-words-1234-56",
        }
    ]

    _test(source, expected)


def test_default_header_anchor_function_multiple_spaces():
    source = """
    = Some    Words     1234    56
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Some    Words     1234    56",
            "level": 1,
            "anchor": "some-words-1234-56",
        }
    ]

    _test(source, expected)


def test_default_header_anchor_function_filter_characters():
    source = """
    = Some #Words @ 12!34 56
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Some #Words @ 12!34 56",
            "level": 1,
            "anchor": "some-words-1234-56",
        }
    ]

    _test(source, expected)


def test_custom_header_anchor_function():
    source = """
    = Title of the section
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Title of the section",
            "level": 1,
            "anchor": "XXXXXY",
        }
    ]

    config = {"mau": {"header_anchor_function": lambda text, level: "XXXXXY"}}

    _test = parser_test_factory(MainParser, variables=config)

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_header_level_1(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = """
    = Title of the section
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Title of the section",
            "level": 1,
            "anchor": "XXXXXX",
        }
    ]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_header_level_3(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = """
    === Title of a subsection
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Title of a subsection",
            "level": 3,
            "anchor": "XXXXXX",
        }
    ]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_collect_headers(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    = Header 1
    == Header 1.1
    == Header 1.2
    = Header 2
    == Header 2.1
    === Header 2.1.1
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1",
            "level": 1,
            "anchor": "Header 1-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1.1",
            "level": 2,
            "anchor": "Header 1.1-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1.2",
            "level": 2,
            "anchor": "Header 1.2-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 2",
            "level": 1,
            "anchor": "Header 2-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 2.1",
            "level": 2,
            "anchor": "Header 2.1-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 2.1.1",
            "level": 3,
            "anchor": "Header 2.1.1-XXXXXX",
        },
    ]

    p = _test(source, expected)

    assert p.headers == [
        nodes.HeaderNode("Header 1", 1, "Header 1-XXXXXX"),
        nodes.HeaderNode("Header 1.1", 2, "Header 1.1-XXXXXX"),
        nodes.HeaderNode("Header 1.2", 2, "Header 1.2-XXXXXX"),
        nodes.HeaderNode("Header 2", 1, "Header 2-XXXXXX"),
        nodes.HeaderNode("Header 2.1", 2, "Header 2.1-XXXXXX"),
        nodes.HeaderNode("Header 2.1.1", 3, "Header 2.1.1-XXXXXX"),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_attributes_header(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    [value1,someattr1=somevalue1,someattr2=somevalue2]
    = Header
    """

    expected = [
        {
            "type": "header",
            "value": "Header",
            "level": 1,
            "kwargs": {"someattr1": "somevalue1", "someattr2": "somevalue2"},
            "tags": [],
            "anchor": "Header-XXXXXX",
        },
    ]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_single_tag_header(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    [tags=section]
    = Header
    """

    expected = [
        {
            "type": "header",
            "value": "Header",
            "level": 1,
            "kwargs": {},
            "tags": ["section"],
            "anchor": "Header-XXXXXX",
        },
    ]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_multiple_tags_header(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    [tags="section,important"]
    = Header
    """

    expected = [
        {
            "type": "header",
            "value": "Header",
            "level": 1,
            "kwargs": {},
            "tags": ["section", "important"],
            "anchor": "Header-XXXXXX",
        },
    ]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_attributes_and_tags_header(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    [value1,someattr1=somevalue1,someattr2=somevalue2,tags="section,important"]
    = Header
    """

    expected = [
        {
            "type": "header",
            "value": "Header",
            "level": 1,
            "kwargs": {"someattr1": "somevalue1", "someattr2": "somevalue2"},
            "tags": ["section", "important"],
            "anchor": "Header-XXXXXX",
        },
    ]

    _test(source, expected)


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_headers_not_in_toc(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    = Header 1
    == Header 1.1
    ==! Header 1.2
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1",
            "level": 1,
            "anchor": "Header 1-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1.1",
            "level": 2,
            "anchor": "Header 1.1-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1.2",
            "level": 2,
            "anchor": "Header 1.2-XXXXXX",
        },
    ]

    p = _test(source, expected)

    assert p.headers == [
        nodes.HeaderNode("Header 1", 1, "Header 1-XXXXXX"),
        nodes.HeaderNode("Header 1.1", 2, "Header 1.1-XXXXXX"),
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_headers_not_in_toc_with_children(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    source = """
    = Header 1
    == Header 1.1
    ==! Header 1.2
    === Header 1.2.1
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1",
            "level": 1,
            "anchor": "Header 1-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1.1",
            "level": 2,
            "anchor": "Header 1.1-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1.2",
            "level": 2,
            "anchor": "Header 1.2-XXXXXX",
        },
        {
            "type": "header",
            "kwargs": {},
            "tags": [],
            "value": "Header 1.2.1",
            "level": 3,
            "anchor": "Header 1.2.1-XXXXXX",
        },
    ]

    p = _test(source, expected)

    assert p.headers == [
        nodes.HeaderNode("Header 1", 1, "Header 1-XXXXXX"),
        nodes.HeaderNode("Header 1.1", 2, "Header 1.1-XXXXXX"),
        nodes.HeaderNode("Header 1.2.1", 3, "Header 1.2.1-XXXXXX"),
    ]
