from unittest.mock import patch

from mau.parsers.text_parser import TextParser

from tests.helpers import listasdict, init_parser_factory, parser_test_factory

init_parser = init_parser_factory(TextParser)

_test = parser_test_factory(TextParser)


def test_collect_macro_arguments_single_argument():
    source = "(value1)"

    p = init_parser(source)
    assert p._collect_macro_args() == "value1"


def test_collect_macro_arguments_multiple_arguments():
    source = "(value1,value2)"

    p = init_parser(source)
    assert p._collect_macro_args() == "value1,value2"


def test_collect_macro_arguments_single_argument_with_quotes():
    source = '("value1")'

    p = init_parser(source)
    assert p._collect_macro_args() == '"value1"'


def test_collect_macro_arguments_single_argument_with_quotes_and_parenthesis():
    source = '("value1()")'

    p = init_parser(source)
    assert p._collect_macro_args() == '"value1()"'


def test_collect_macro_arguments_single_argument_with_parenthesis():
    source = "(value1())"

    p = init_parser(source)
    assert p._collect_macro_args() == "value1("


def test_collect_macro_arguments_multiple_argument_with_quotes_and_parenthesis():
    source = '("value1()",value2,value3)'

    p = init_parser(source)
    assert p._collect_macro_args() == '"value1()",value2,value3'


def test_macro():
    source = "[macroname](value1,value2)"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "macro",
                    "name": "macroname",
                    "value": "value1",
                    "args": ["value1", "value2"],
                    "kwargs": {},
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_arguments_with_quotes():
    source = '[macroname]("value1,value2")'

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "macro",
                    "name": "macroname",
                    "value": "value1,value2",
                    "args": ["value1,value2"],
                    "kwargs": {},
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_named_arguments():
    source = "[macroname](name,arg1=value1)"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "macro",
                    "name": "macroname",
                    "value": "name",
                    "args": ["name"],
                    "kwargs": {"arg1": "value1"},
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_link():
    source = '[link](https://somedomain.org/the/path, "link text")'

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path",
                    "text": "link text",
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_link_with_quotes():
    source = '[link](https://somedomain.org/the/path,"link, text")'

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path",
                    "text": "link, text",
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_link_with_escaped_quotes():
    source = r'[link](https://somedomain.org/the/path,"link \"text\"")'

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path",
                    "text": 'link "text"',
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_link_with_escaped_round_braces():
    source = '[link](https://somedomain.org/the/path,"link (text\\)")'

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path",
                    "text": "link (text)",
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_link_with_escaped_round_braces_in_the_url():
    source = '[link](https://somedomain.org/the/path_(note\\),"link")'

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path_(note)",
                    "text": "link",
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_link_with_quotes_and_round_braces_in_the_url():
    source = '[link]("https://somedomain.org/the/path_(note)","link")'

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path_(note)",
                    "text": "link",
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_link_without_text():
    source = "[link](https://somedomain.org/the/path)"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path",
                    "text": "https://somedomain.org/the/path",
                }
            ],
        }
    ]

    _test(source, expected)


def test_automatic_link():
    source = "This is https://somedomain.org/the/path text"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "This is "},
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path",
                    "text": "https://somedomain.org/the/path",
                },
                {"type": "text", "value": " text"},
            ],
        }
    ]

    _test(source, expected)


def test_automatic_link_ending_with_period():
    source = "The link is https://somedomain.org/the/path."

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "The link is "},
                {
                    "type": "link",
                    "target": "https://somedomain.org/the/path",
                    "text": "https://somedomain.org/the/path",
                },
                {"type": "text", "value": "."},
            ],
        }
    ]

    _test(source, expected)


def test_http_mentions():
    source = "Dangerous words: http and https"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "Dangerous words: http and https"},
            ],
        }
    ]

    _test(source, expected)


def test_macro_image():
    source = "[image](/the/path.jpg)"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "image",
                    "uri": "/the/path.jpg",
                    "alt_text": None,
                    "width": None,
                    "height": None,
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_image_with_alt_text():
    source = '[image](/the/path.jpg,"alt name")'

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "image",
                    "uri": "/the/path.jpg",
                    "alt_text": "alt name",
                    "width": None,
                    "height": None,
                }
            ],
        }
    ]

    _test(source, expected)


def test_macro_image_with_width_and_height():
    source = "[image](/the/path.jpg,width=120,height=120)"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "image",
                    "uri": "/the/path.jpg",
                    "alt_text": None,
                    "width": "120",
                    "height": "120",
                }
            ],
        }
    ]

    _test(source, expected)


@patch("mau.parsers.text_parser.footnote_anchors")
def test_macro_footnote(footnote_anchors_mock):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")

    source = "[footnote](Some text _and style_ and *more style* here)"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "footnote_ref",
                    "number": 1,
                    "refanchor": "refXYZ",
                    "defanchor": "defXYZ",
                    "content": [
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
                    ],
                }
            ],
        }
    ]

    p = _test(source, expected)

    assert listasdict(p.footnote_defs) == [
        {
            "type": "footnote_def",
            "number": 1,
            "refanchor": "refXYZ",
            "defanchor": "defXYZ",
            "content": [
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
            ],
        }
    ]


@patch("mau.parsers.text_parser.footnote_anchors")
def test_parse_macro_footnote_can_start_with_different_number(footnote_anchors_mock):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")

    p = init_parser(
        "[footnote](Some text _and style_ and *more style* here)",
        footnotes_start_with=6,
    )
    result = p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "footnote_ref",
                    "number": 6,
                    "refanchor": "refXYZ",
                    "defanchor": "defXYZ",
                    "content": [
                        {
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
                            "type": "sentence",
                        },
                    ],
                }
            ],
        }
    ]


@patch("mau.parsers.text_parser.footnote_anchors")
def test_parse_macro_footnote_with_other_text_around(footnote_anchors_mock):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")

    source = "text[footnote](Some text) other text"

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "text"},
                {
                    "type": "footnote_ref",
                    "number": 1,
                    "refanchor": "refXYZ",
                    "defanchor": "defXYZ",
                    "content": [
                        {
                            "type": "sentence",
                            "content": [
                                {"type": "text", "value": "Some text"},
                            ],
                        }
                    ],
                },
                {"type": "text", "value": " other text"},
            ],
        }
    ]

    p = _test(source, expected)

    assert listasdict(p.footnote_defs) == [
        {
            "type": "footnote_def",
            "number": 1,
            "refanchor": "refXYZ",
            "defanchor": "defXYZ",
            "content": [
                {
                    "type": "sentence",
                    "content": [
                        {"type": "text", "value": "Some text"},
                    ],
                }
            ],
        }
    ]


@patch("mau.parsers.text_parser.footnote_anchors")
def test_parse_macro_footnote_includes_round_brakets(footnote_anchors_mock):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")

    source = r'text[footnote]("Some code()") other text'

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "text"},
                {
                    "type": "footnote_ref",
                    "number": 1,
                    "refanchor": "refXYZ",
                    "defanchor": "defXYZ",
                    "content": [
                        {
                            "type": "sentence",
                            "content": [
                                {"type": "text", "value": "Some code()"},
                            ],
                        }
                    ],
                },
                {"type": "text", "value": " other text"},
            ],
        }
    ]

    p = _test(source, expected)

    assert listasdict(p.footnote_defs) == [
        {
            "type": "footnote_def",
            "number": 1,
            "refanchor": "refXYZ",
            "defanchor": "defXYZ",
            "content": [
                {
                    "type": "sentence",
                    "content": [
                        {"type": "text", "value": "Some code()"},
                    ],
                }
            ],
        }
    ]


@patch("mau.parsers.text_parser.footnote_anchors")
def test_parse_macro_footnote_commas_mau_v1(
    footnote_anchors_mock,
):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")

    source = r"text[footnote](Some text, that should not, be split) other text"

    _test = parser_test_factory(TextParser, v1_backward_compatibility=True)

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "text"},
                {
                    "type": "footnote_ref",
                    "number": 1,
                    "refanchor": "refXYZ",
                    "defanchor": "defXYZ",
                    "content": [
                        {
                            "type": "sentence",
                            "content": [
                                {
                                    "type": "text",
                                    "value": "Some text, that should not, be split",
                                },
                            ],
                        }
                    ],
                },
                {"type": "text", "value": " other text"},
            ],
        }
    ]

    p = _test(source, expected)

    assert listasdict(p.footnote_defs) == [
        {
            "type": "footnote_def",
            "number": 1,
            "refanchor": "refXYZ",
            "defanchor": "defXYZ",
            "content": [
                {
                    "type": "sentence",
                    "content": [
                        {
                            "type": "text",
                            "value": "Some text, that should not, be split",
                        },
                    ],
                }
            ],
        }
    ]


@patch("mau.parsers.text_parser.footnote_anchors")
def test_parse_macro_footnote_commas_mau_v2(
    footnote_anchors_mock,
):
    footnote_anchors_mock.return_value = ("refXYZ", "defXYZ")

    source = r'text[footnote]("Some text, that should not, be split") other text'

    _test = parser_test_factory(TextParser)

    expected = [
        {
            "type": "sentence",
            "content": [
                {"type": "text", "value": "text"},
                {
                    "type": "footnote_ref",
                    "number": 1,
                    "refanchor": "refXYZ",
                    "defanchor": "defXYZ",
                    "content": [
                        {
                            "type": "sentence",
                            "content": [
                                {
                                    "type": "text",
                                    "value": "Some text, that should not, be split",
                                },
                            ],
                        }
                    ],
                },
                {"type": "text", "value": " other text"},
            ],
        }
    ]

    p = _test(source, expected)

    assert listasdict(p.footnote_defs) == [
        {
            "type": "footnote_def",
            "number": 1,
            "refanchor": "refXYZ",
            "defanchor": "defXYZ",
            "content": [
                {
                    "type": "sentence",
                    "content": [
                        {
                            "type": "text",
                            "value": "Some text, that should not, be split",
                        },
                    ],
                }
            ],
        }
    ]


def test_parse_macro_mailto():
    source = "[mailto](info@projectmau.org)"

    expected = [
        {
            "type": "sentence",
            "content": [
                {
                    "type": "link",
                    "target": "mailto:info@projectmau.org",
                    "text": "info@projectmau.org",
                }
            ],
        }
    ]

    _test(source, expected)


def test_single_class():
    source = 'Some text [class]("text with that class", classname)'

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
    source = 'Some text [class]("text with that class", "classname1,classname2")'

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


def test_parse_class_with_rich_text():
    source = '[class]("Some text with `verbatim words` and _styled ones_", classname)'

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
