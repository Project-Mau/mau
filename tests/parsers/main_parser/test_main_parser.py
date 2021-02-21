import pytest

from mau.parsers.base_parser import ParseError
from mau.parsers.main_parser import MainParser

from tests.helpers import listasdict, init_parser_factory, parser_test_factory, dedent

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


def test_parse_discards_empty_lines():
    _test("\n\n\n\n", [])


def test_horizontal_rule():
    _test("---", [{"type": "horizontal_rule"}])


def test_parse_single_line_comments():
    _test("// Just a comment", [])


def test_parse_multi_line_comments():
    p = init_parser(
        dedent(
            """
            ////
            This is a
            multiline
            comment
            ////
            """
        )
    )
    p.parse()

    assert listasdict(p.nodes) == []


def test_parse_multi_line_comments_with_dangerous_characters():
    source = """
    ////
    .This is a
    [multiline]
    ----
    comment
    ////
    """

    _test(source, [])


def test_parse_open_multi_line_comments():
    p = init_parser(
        dedent(
            """
            ////
            This is a
            multiline
            comment
            """
        )
    )

    with pytest.raises(ParseError):
        p.parse()


def test_parse_paragraphs_starting_with_a_macro():
    p = init_parser("[link](http://some.where,text) is the link I want")
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "link",
                        "text": "text",
                        "target": "http://some.where",
                    },
                    {
                        "type": "text",
                        "value": " is the link I want",
                    },
                ],
            },
        },
    ]


def test_parse_paragraphs_is_a_macro_only():
    p = init_parser("[link](http://some.where,text)")
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "paragraph",
            "args": [],
            "kwargs": {},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "link",
                        "text": "text",
                        "target": "http://some.where",
                    },
                ],
            },
        },
    ]


def test_command():
    p = init_parser("::somecommand:argument1=value1,argument2=value2")
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "command",
            "name": "somecommand",
            "kwargs": {"argument1": "value1", "argument2": "value2"},
        },
    ]


def test_command_without_arguments():
    p = init_parser("::somecommand:")
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "command",
            "name": "somecommand",
            "kwargs": {},
        },
    ]


def test_attributes_paragraph():
    p = init_parser(
        dedent(
            """
            [value1,someattr1=somevalue1,someattr2=somevalue2]
            This is text
            """
        )
    )
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "paragraph",
            "args": ["value1"],
            "kwargs": {"someattr1": "somevalue1", "someattr2": "somevalue2"},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This is text",
                    }
                ],
            },
        },
    ]


def test_attributes_with_variables():
    p = init_parser(
        dedent(
            """
            :attrs:value1,someattr1=somevalue1,someattr2=somevalue2

            [{attrs}]
            This is text
            """
        )
    )
    p.parse()

    assert listasdict(p.nodes) == [
        {
            "type": "paragraph",
            "args": ["value1"],
            "kwargs": {"someattr1": "somevalue1", "someattr2": "somevalue2"},
            "content": {
                "type": "sentence",
                "content": [
                    {
                        "type": "text",
                        "value": "This is text",
                    }
                ],
            },
        },
    ]


def test_simple_paragraph():
    source = """
    This is a simple line of text
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
                        "value": "This is a simple line of text",
                    }
                ],
            },
        }
    ]

    _test(source, expected)


def test_multiline_paragraph():
    source = """
    This is a simple line of text
    followed by another line of text
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
                        "value": "This is a simple line of text followed by another line of text",
                    }
                ],
            },
        }
    ]

    _test(source, expected)


def test_multiple_paragraphs():
    source = """
    This is a simple line of text
    followed by another line of text

    And this is another paragraph
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
    ]

    _test(source, expected)


def test_style_underscore():
    source = """
    This is _underscore_ text
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
                        "value": "This is ",
                    },
                    {
                        "type": "style",
                        "value": "underscore",
                        "content": {
                            "type": "sentence",
                            "content": [{"type": "text", "value": "underscore"}],
                        },
                    },
                    {
                        "type": "text",
                        "value": " text",
                    },
                ],
            },
        }
    ]

    _test(source, expected)


def test_style_star():
    source = """
    This is *star* text
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
                        "value": "This is ",
                    },
                    {
                        "type": "style",
                        "value": "star",
                        "content": {
                            "type": "sentence",
                            "content": [{"type": "text", "value": "star"}],
                        },
                    },
                    {
                        "type": "text",
                        "value": " text",
                    },
                ],
            },
        }
    ]

    _test(source, expected)


def test_style_at_beginning():
    source = """
    *This is star text*
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
                        "type": "style",
                        "value": "star",
                        "content": {
                            "type": "sentence",
                            "content": [{"type": "text", "value": "This is star text"}],
                        },
                    },
                ],
            },
        }
    ]

    _test(source, expected)


def test_style_not_closed():
    source = r"""
    This ` is a backtick and this _an underscore
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
                        "value": "This ` is a backtick and this _an underscore",
                    },
                ],
            },
        }
    ]

    _test(source, expected)


def test_style_escape_markers():
    source = r"""
    This is \_underscore\_ and this is \`verbatim\`
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
                        "value": "This is _underscore_ and this is `verbatim`",
                    },
                ],
            },
        }
    ]

    _test(source, expected)
