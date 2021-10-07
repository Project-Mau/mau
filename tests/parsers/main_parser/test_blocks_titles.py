from unittest.mock import patch

from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_test_factory

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_title_block():
    source = """
    . This is the title
    ----
    This is a simple line of text
    followed by another line of text

    And this is another paragraph
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": None,
            "kwargs": {},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This is the title",
                    }
                ],
            },
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a simple line of text followed by another line of text",
                            }
                        ],
                    },
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
                                "value": "And this is another paragraph",
                            }
                        ],
                    },
                },
            ],
        },
    ]

    _test(source, expected)


def test_title_without_spaces():
    source = """
    .This is the title
    ----
    This is a simple line of text
    followed by another line of text

    And this is another paragraph
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": None,
            "kwargs": {},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This is the title",
                    }
                ],
            },
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a simple line of text followed by another line of text",
                            }
                        ],
                    },
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
                                "value": "And this is another paragraph",
                            }
                        ],
                    },
                },
            ],
        },
    ]

    _test(source, expected)


def test_title_with_rich_text():
    source = """
    . This _is_ the title
    ----
    This is a simple line of text
    followed by another line of text

    And this is another paragraph
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": None,
            "kwargs": {},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This ",
                    },
                    {
                        "type": "style",
                        "value": "underscore",
                        "content": {
                            "type": "sentence",
                            "content": [
                                {
                                    "type": "text",
                                    "value": "is",
                                }
                            ],
                        },
                    },
                    {
                        "type": "text",
                        "value": " the title",
                    },
                ],
            },
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a simple line of text followed by another line of text",
                            }
                        ],
                    },
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
                                "value": "And this is another paragraph",
                            }
                        ],
                    },
                },
            ],
        },
    ]

    _test(source, expected)


def test_title_block_with_attributes():
    source = """
    . This is the title
    [blocktype,attr1=value1]
    ----
    This is a simple line of text
    followed by another line of text

    And this is another paragraph
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {"attr1": "value1"},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This is the title",
                    }
                ],
            },
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a simple line of text followed by another line of text",
                            }
                        ],
                    },
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
                                "value": "And this is another paragraph",
                            }
                        ],
                    },
                },
            ],
        },
    ]

    _test(source, expected)


@patch("mau.parsers.text_parser.footnote_anchors")
def test_title_block_with_footnote(footnote_anchors_mock):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")

    source = """
    . This is the title[footnote](just some text)
    ----
    This is a simple line of text
    followed by another line of text

    And this is another paragraph
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": None,
            "kwargs": {},
            "secondary_content": [],
            "classes": [],
            "engine": "default",
            "preprocessor": "none",
            "title": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This is the title",
                    },
                    {
                        "content": [
                            {
                                "content": [
                                    {"type": "text", "value": "just some text"}
                                ],
                                "type": "sentence",
                            },
                        ],
                        "defanchor": "defXYZ",
                        "number": 1,
                        "refanchor": "refXYZ",
                        "type": "footnote_ref",
                    },
                ],
            },
            "content": [
                {
                    "type": "paragraph",
                    "args": [],
                    "kwargs": {},
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "text",
                                "value": "This is a simple line of text followed by another line of text",
                            }
                        ],
                    },
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
                                "value": "And this is another paragraph",
                            }
                        ],
                    },
                },
            ],
        },
    ]

    _test(source, expected)
