import pytest

from mau.parsers.base_parser import ParserError
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_test_factory

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_parse_block_with_empty_body():
    source = """
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": None,
            "content": [],
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_parse_block_content():
    source = """
    ----
    This is a paragraph.
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": None,
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a paragraph.",
                            },
                        ],
                        "type": "sentence",
                    },
                },
            ],
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_parse_block_content_variables():
    source = """
    ----
    :answer:42
    The answer is {answer}.
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": None,
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "content": [
                            {
                                "type": "text",
                                "value": "The answer is 42.",
                            },
                        ],
                        "type": "sentence",
                    },
                },
            ],
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_parse_block_content_external_variables():
    source = """
    :answer:42
    ----
    The answer is {answer}.
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": None,
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "content": [
                            {
                                "type": "text",
                                "value": "The answer is 42.",
                            },
                        ],
                        "type": "sentence",
                    },
                },
            ],
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_block_without_closing_fences():
    p = init_parser("----")

    with pytest.raises(ParserError):
        p.parse()


def test_parse_block_secondary_content():
    source = """
    ----
    ----
    This is a paragraph that gets eaten.
    This is a second paragraph that gets eaten.
    
    This paragraph appears in the output.
    """

    expected = [
        {
            "type": "block",
            "title": None,
            "blocktype": None,
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
            "content": [],
            "secondary_content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a paragraph that gets eaten. This is a second paragraph that gets eaten.",
                            },
                        ],
                        "type": "sentence",
                    },
                },
            ],
        },
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This paragraph appears in the output.",
                    }
                ],
            },
        },
    ]

    _test(source, expected)


def test_parse_block_inside_block():
    source = """
    ----
    ++++
    ++++
    ----
    """

    expected = [
        {
            "type": "block",
            "title": None,
            "blocktype": None,
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "args": [],
            "kwargs": {},
            "secondary_content": [],
            "content": [
                {
                    "type": "block",
                    "blocktype": None,
                    "title": None,
                    "content": [],
                    "secondary_content": [],
                    "classes": [],
                    "engine": "default",
                    "preprocessor": "none",
                    "args": [],
                    "kwargs": {},
                },
            ],
        }
    ]

    _test(source, expected)
