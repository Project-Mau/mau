import pytest
from mau.lexers.main_lexer import MainLexer
from mau.nodes.footnotes import CommandFootnotesNode
from mau.nodes.inline import LinkNode, SentenceNode, StyleNode, TextNode
from mau.nodes.page import CommandTocNode, HorizontalRuleNode, ParagraphNode
from mau.parsers.base_parser import ParserError
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

# from mau.parsers.base_parser import ParserError


init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_parse_discards_empty_lines():
    source = "\n\n\n\n"

    assert runner(source).nodes == []


def test_horizontal_rule():
    source = "---"

    expected = [HorizontalRuleNode()]

    assert runner(source).nodes == expected


def test_horizontal_rule_with_arguments():
    source = """
    [break,arg1=value1]
    ---
    """

    expected = [
        HorizontalRuleNode(args=["break"], kwargs={"arg1": "value1"}),
    ]

    assert runner(source).nodes == expected


def test_parse_single_line_comments():
    source = "// Just a comment"

    assert runner(source).nodes == []


def test_parse_multi_line_comments():
    source = """
    ////
    This is a
    multiline
    comment
    ////
    """

    assert runner(source).nodes == []


def test_parse_multi_line_comments_with_dangerous_characters():
    source = """
    ////
    .This is a
    [multiline]
    ----
    comment
    ////
    """

    assert runner(source).nodes == []


def test_parse_open_multi_line_comments():
    source = """
    ////
    .This is a
    [multiline]
    ----
    comment
    """

    with pytest.raises(ParserError):
        runner(source)


def test_parse_paragraphs():
    source = """
    This is a paragraph.
    This is part of the same paragraph.

    This is a new paragraph.
    """

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    TextNode(
                        "This is a paragraph. This is part of the same paragraph."
                    ),
                ]
            ),
            args=[],
            kwargs={},
        ),
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This is a new paragraph."),
                ]
            ),
            args=[],
            kwargs={},
        ),
    ]


def test_parse_paragraph_starting_with_a_macro():
    source = "[link](http://some.where,This) is the link I want"

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    LinkNode(target="http://some.where", text="This"),
                    TextNode(" is the link I want"),
                ]
            )
        )
    ]


def test_attributes():
    source = "[value1,someattr1=somevalue1,someattr2=somevalue2]"

    parser = init_parser(source)
    parser.parse()

    assert parser.arguments == (
        ["value1"],
        {
            "someattr1": "somevalue1",
            "someattr2": "somevalue2",
        },
        [],
    )


def test_attributes_paragraph():
    source = """
    [value1,someattr1=somevalue1,someattr2=somevalue2]
    This is text
    """

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [TextNode("This is text")],
            ),
            args=["value1"],
            kwargs={"someattr1": "somevalue1", "someattr2": "somevalue2"},
        ),
    ]


def test_attributes_with_variables():
    source = """
    :attrs:value1,someattr1=somevalue1,someattr2=somevalue2

    [{attrs}]
    This is text
    """

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [TextNode("This is text")],
            ),
            args=["value1"],
            kwargs={"someattr1": "somevalue1", "someattr2": "somevalue2"},
        ),
    ]


def test_command():
    source = "::somecommand:arg1, arg2, name1=value1, name2=value2"

    assert runner(source).nodes == []


def test_command_without_arguments():
    source = "::somecommand:"

    assert runner(source).nodes == []


def test_command_toc():
    source = "::toc:arg1, arg2, #tag1, name1=value1, name2=value2"

    assert runner(source).nodes == [
        CommandTocNode(
            [],
            args=["arg1", "arg2"],
            kwargs={"name1": "value1", "name2": "value2"},
            tags=["tag1"],
        ),
    ]


def test_command_footnotes():
    source = "::footnotes:arg1, arg2, #tag1, name1=value1, name2=value2"

    parser = init_parser(source)
    parser.footnote_entries = []
    parser.parse()

    assert parser.nodes == [
        CommandFootnotesNode(
            parser.footnote_entries,
            args=["arg1", "arg2"],
            kwargs={"name1": "value1", "name2": "value2"},
            tags=["tag1"],
        ),
    ]


def test_style_underscore():
    source = """
    This is _underscore_ text
    """

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This is "),
                    StyleNode(
                        "underscore",
                        SentenceNode(
                            [
                                TextNode("underscore"),
                            ],
                        ),
                    ),
                    TextNode(" text"),
                ],
            )
        )
    ]


def test_style_at_beginning():
    source = """
    *This is star text*
    """

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    StyleNode(
                        "star",
                        SentenceNode(
                            [
                                TextNode("This is star text"),
                            ]
                        ),
                    ),
                ],
            )
        )
    ]


def test_style_not_closed():
    source = r"""
    This ` is a backtick and this _an underscore
    """

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This ` is a backtick and this _an underscore"),
                ],
            )
        )
    ]


def test_style_escape_markers():
    source = r"""
    This is \_underscore\_ and this is \`verbatim\`
    """

    assert runner(source).nodes == [
        ParagraphNode(
            SentenceNode(
                [
                    TextNode("This is _underscore_ and this is `verbatim`"),
                ],
            )
        )
    ]
