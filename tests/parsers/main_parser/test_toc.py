from unittest.mock import patch

from mau.parsers.main_parser import MainParser

from tests.helpers import listasdict, init_parser_factory, parser_test_factory, dedent

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


@patch("mau.parsers.main_parser.header_anchor")
def test_create_toc(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    p = init_parser(
        dedent(
            """
            = Header 1
            == Header 1.1
            == Header 1.2
            = Header 2
            == Header 2.1
            === Header 2.1.1
            """
        )
    )
    p.parse()

    assert listasdict(p.toc) == [
        {
            "type": "toc_entry",
            "level": 1,
            "text": "Header 1",
            "anchor": "Header 1-XXXXXX",
            "children": [
                {
                    "type": "toc_entry",
                    "level": 2,
                    "text": "Header 1.1",
                    "anchor": "Header 1.1-XXXXXX",
                    "children": [],
                },
                {
                    "type": "toc_entry",
                    "level": 2,
                    "text": "Header 1.2",
                    "anchor": "Header 1.2-XXXXXX",
                    "children": [],
                },
            ],
        },
        {
            "type": "toc_entry",
            "level": 1,
            "text": "Header 2",
            "anchor": "Header 2-XXXXXX",
            "children": [
                {
                    "type": "toc_entry",
                    "level": 2,
                    "text": "Header 2.1",
                    "anchor": "Header 2.1-XXXXXX",
                    "children": [
                        {
                            "type": "toc_entry",
                            "level": 3,
                            "text": "Header 2.1.1",
                            "anchor": "Header 2.1.1-XXXXXX",
                            "children": [],
                        },
                    ],
                },
            ],
        },
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_create_toc_ignore_headers(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    p = init_parser(
        dedent(
            """
            = Header 1
            ==! Header 1.1
            ==! Header 1.2
            = Header 2
            ==! Header 2.1
            ===! Header 2.1.1
            """
        )
    )
    p.parse()

    assert listasdict(p.toc) == [
        {
            "type": "toc_entry",
            "level": 1,
            "text": "Header 1",
            "anchor": "Header 1-XXXXXX",
            "children": [],
        },
        {
            "type": "toc_entry",
            "level": 1,
            "text": "Header 2",
            "anchor": "Header 2-XXXXXX",
            "children": [],
        },
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_create_toc_orphan_nodes(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    p = init_parser(
        dedent(
            """
            = Header 1
            === Header 1.1.1
            == Header 1.2
            """
        )
    )
    p.parse()

    assert [i.asdict() for i in p.toc] == [
        {
            "type": "toc_entry",
            "level": 1,
            "text": "Header 1",
            "anchor": "Header 1-XXXXXX",
            "children": [
                {
                    "type": "toc_entry",
                    "level": 3,
                    "text": "Header 1.1.1",
                    "anchor": "Header 1.1.1-XXXXXX",
                    "children": [],
                },
                {
                    "type": "toc_entry",
                    "level": 2,
                    "text": "Header 1.2",
                    "anchor": "Header 1.2-XXXXXX",
                    "children": [],
                },
            ],
        },
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_header_not_in_toc(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = """
    =! Title of the section
    """

    expected = [
        {
            "type": "header",
            "kwargs": {},
            "value": "Title of the section",
            "level": 1,
            "anchor": "XXXXXX",
        }
    ]

    p = _test(source, expected)

    assert listasdict(p.toc) == []
