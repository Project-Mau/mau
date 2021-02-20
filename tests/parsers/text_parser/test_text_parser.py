from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_test_factory

init_parser = init_parser_factory(TextParser)

_test = parser_test_factory(TextParser)


def test_empty_text():
    source = ""

    expected = [
        {
            "type": "sentence",
            "content": [],
        }
    ]

    _test(source, expected)


def test_multiple_words():
    source = "Many different words"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "Many different words"},
            ],
        }
    ]

    _test(source, expected)


def test_underscore():
    source = "_Some text_"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "style",
                    "value": "underscore",
                    "content": {
                        "type": "sentence",
                        "content": [{"type": "text", "value": "Some text"}],
                    },
                }
            ],
        }
    ]

    _test(source, expected)


def test_star():
    source = "*Some text*"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "style",
                    "value": "star",
                    "content": {
                        "type": "sentence",
                        "content": [{"type": "text", "value": "Some text"}],
                    },
                }
            ],
        }
    ]

    _test(source, expected)


def test_style_within_style():
    source = "_*Words with two styles*_"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "style",
                    "value": "underscore",
                    "content": {
                        "type": "sentence",
                        "content": [
                            {
                                "type": "style",
                                "value": "star",
                                "content": {
                                    "type": "sentence",
                                    "content": [
                                        {
                                            "type": "text",
                                            "value": "Words with two styles",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                }
            ],
        }
    ]

    _test(source, expected)


def test_paragraph_double_style_cancels_itself():
    source = "__Text__"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "style",
                    "value": "underscore",
                    "content": {"type": "sentence", "content": []},
                },
                {"type": "text", "value": "Text"},
                {
                    "type": "style",
                    "value": "underscore",
                    "content": {"type": "sentence", "content": []},
                },
            ],
        }
    ]

    _test(source, expected)


def test_text_and_styles():
    source = "Some text _and style_ and *more style* here"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "Some text "},
                {
                    "type": "style",
                    "value": "underscore",
                    "content": {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "and style"},
                        ],
                    },
                },
                {"type": "text", "value": " and "},
                {
                    "type": "style",
                    "value": "star",
                    "content": {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "more style"},
                        ],
                    },
                },
                {"type": "text", "value": " here"},
            ],
        }
    ]

    _test(source, expected)


def test_parse_style_open():
    source = "_Text"

    expected = [
        {
            "type": "sentence",
            "content": [{"type": "text", "value": "_Text"}],
        },
    ]

    _test(source, expected)


def test_verbatim():
    source = "`Many different words`"

    expected = [
        {
            "type": "sentence",
            "content": [{"type": "verbatim", "value": "Many different words"}],
        }
    ]

    _test(source, expected)


def test_verbatim_backtick():
    source = r"`\``"

    expected = [
        {
            "type": "sentence",
            "content": [{"type": "verbatim", "value": "`"}],
        }
    ]

    _test(source, expected)


def test_verbatim_ignore_style():
    source = "`_Many different words_`"

    expected = [
        {
            "type": "sentence",
            "content": [{"type": "verbatim", "value": "_Many different words_"}],
        }
    ]

    _test(source, expected)


def test_verbatim_open():
    source = "`Many different words"

    expected = [
        {
            "type": "sentence",
            "content": [{"type": "text", "value": "`Many different words"}],
        }
    ]

    _test(source, expected)


def test_verbatim_and_style():
    source = "Some text with `verbatim words` and _styled ones_"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "Some text with "},
                {"type": "verbatim", "value": "verbatim words"},
                {"type": "text", "value": " and "},
                {
                    "type": "style",
                    "value": "underscore",
                    "content": {
                        "type": "sentence",
                        "content": [{"type": "text", "value": "styled ones"}],
                    },
                },
            ],
        }
    ]

    _test(source, expected)


def test_parse_class_with_rich_text():
    source = "[classname]#Some text with `verbatim words` and _styled ones_#"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "class",
                    "classes": ["classname"],
                    "content": {
                        "type": "sentence",
                        "content": [
                            {"type": "text", "value": "Some text with "},
                            {"type": "verbatim", "value": "verbatim words"},
                            {"type": "text", "value": " and "},
                            {
                                "type": "style",
                                "value": "underscore",
                                "content": {
                                    "type": "sentence",
                                    "content": [
                                        {"type": "text", "value": "styled ones"}
                                    ],
                                },
                            },
                        ],
                    },
                }
            ],
        }
    ]

    _test(source, expected)


def test_single_class():
    source = "Some text [classname]#text with that class#"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "Some text "},
                {
                    "type": "class",
                    "classes": ["classname"],
                    "content": {
                        "type": "sentence",
                        "content": [{"type": "text", "value": "text with that class"}],
                    },
                },
            ],
        }
    ]

    _test(source, expected)


def test_multiple_classes():
    source = "Some text [classname1,classname2]#text with that class#"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "Some text "},
                {
                    "type": "class",
                    "classes": ["classname1", "classname2"],
                    "content": {
                        "type": "sentence",
                        "content": [{"type": "text", "value": "text with that class"}],
                    },
                },
            ],
        }
    ]

    _test(source, expected)


def test_class_with_verbatim_and_class_literal():
    source = "[classname]#`verbatim #`#"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "class",
                    "classes": ["classname"],
                    "content": {
                        "type": "sentence",
                        "content": [
                            {"type": "verbatim", "value": "verbatim #"},
                        ],
                    },
                }
            ],
        }
    ]

    _test(source, expected)


def test_square_brackets():
    source = "This contains [ and ] and [this]"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "This contains [ and ] and [this]"},
            ],
        }
    ]

    _test(source, expected)


def test_escapes():
    source = r"This contains \[this\]#that looks like a class#"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "text",
                    "value": "This contains [this]#that looks like a class#",
                },
            ],
        }
    ]

    _test(source, expected)
