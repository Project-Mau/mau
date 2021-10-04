import pytest

from mau.parsers.main_parser import MainParser, ParseError, EngineError
from mau.parsers.preprocess_variables_parser import PreprocessError

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
            "engine": "mau",
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
            "engine": "mau",
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
            "engine": "mau",
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
            "engine": "mau",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_block_without_closing_fences():
    p = init_parser("----")

    with pytest.raises(ParseError):
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
            "engine": "mau",
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
            "engine": "mau",
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
                    "engine": "mau",
                    "args": [],
                    "kwargs": {},
                },
            ],
        }
    ]

    _test(source, expected)


def test_attributes_block():
    source = """
    [blocktype,myattr1=value1]
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
            "kwargs": {"myattr1": "value1"},
            "secondary_content": [],
            "classes": [],
            "engine": "mau",
            "title": None,
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


def test_attributes_can_contain_variables():
    source = """
    :value:42

    [blocktype,myattr1={value}]
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
            "kwargs": {"myattr1": "42"},
            "secondary_content": [],
            "classes": [],
            "engine": "mau",
            "title": None,
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


def test_parse_block_title_and_attributes():
    source = """
    .Just a title
    [blocktype,attribute1,attribute2]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "blocktype",
            "content": [],
            "secondary_content": [],
            "title": {
                "content": [{"type": "text", "value": "Just a title"}],
                "type": "sentence",
            },
            "classes": [],
            "engine": "mau",
            "args": ["attribute1", "attribute2"],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_parse_block_title_and_attributes_are_reset():
    source = """
    .Just a title
    [blocktype1,attribute1,attribute2]
    ----
    ----

    [blocktype2]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "blocktype1",
            "content": [],
            "secondary_content": [],
            "title": {
                "content": [{"type": "text", "value": "Just a title"}],
                "type": "sentence",
            },
            "classes": [],
            "engine": "mau",
            "args": ["attribute1", "attribute2"],
            "kwargs": {},
        },
        {
            "type": "block",
            "blocktype": "blocktype2",
            "content": [],
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "mau",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_block_classes_single_class():
    source = """
    [blocktype,classes=cls1]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {},
            "secondary_content": [],
            "classes": ["cls1"],
            "engine": "mau",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_classes_multiple_classes():
    source = """
    [blocktype,classes="cls1,cls2"]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {},
            "secondary_content": [],
            "classes": ["cls1", "cls2"],
            "engine": "mau",
            "title": None,
            "content": [],
        },
    ]

    _test(source, expected)


def test_block_engine():
    source = """
    [blocktype,engine=someengine]
    ----
    ----
    """

    expected = [
        {
            "type": "block",
            "args": [],
            "blocktype": "blocktype",
            "kwargs": {},
            "secondary_content": [],
            "classes": [],
            "engine": "someengine",
            "title": None,
            "content": [],
        },
    ]

    with pytest.raises(EngineError):
        _test(source, expected)


def test_block_embedded_mau_has_no_external_variables():
    source = """
    :answer:42
    [block, engine=mau-embedded]
    ----
    The answer is {answer}.
    ----
    """

    expected = [
        {
            "type": "block",
            "blocktype": "block",
            "content": [{"type": "text", "value": "The answer is {answer}."}],
            "secondary_content": [],
            "title": None,
            "classes": [],
            "engine": "mau-embedded",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)


def test_block_raw_engine():
    source = """
    [block, engine=raw]
    ----
    Raw content
    on multiple lines
    ----
    Secondary content
    on multiple lines too
    """

    expected = [
        {
            "type": "block",
            "blocktype": "block",
            "content": [
                {"type": "text", "value": "Raw content"},
                {"type": "text", "value": "on multiple lines"},
            ],
            "secondary_content": [
                {"type": "text", "value": "Secondary content"},
                {"type": "text", "value": "on multiple lines too"},
            ],
            "title": None,
            "classes": [],
            "engine": "raw",
            "args": [],
            "kwargs": {},
        },
    ]

    _test(source, expected)
