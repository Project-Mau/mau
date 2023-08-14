from mau.lexers.text_lexer import TextLexer
from mau.nodes.footnotes import FootnoteNode
from mau.nodes.inline import (
    ClassNode,
    ImageNode,
    LinkNode,
    MacroNode,
    SentenceNode,
    StyleNode,
    TextNode,
    VerbatimNode,
)
from mau.nodes.references import ReferenceNode
from mau.parsers.text_parser import TextParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(TextLexer, TextParser)

runner = parser_runner_factory(TextLexer, TextParser)


def test_empty_text():
    source = ""

    assert runner(source).nodes == []


def test_parse_word():
    source = "Word"

    expected = [
        SentenceNode(
            [
                TextNode("Word"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_multiple_words():
    source = "Many different words"

    expected = [
        SentenceNode(
            [
                TextNode("Many different words"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_parse_escape_word():
    source = r"\Escaped"

    expected = [
        SentenceNode(
            [
                TextNode("Escaped"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_parse_escape_symbol():
    source = r"\"Escaped"

    expected = [
        SentenceNode(
            [
                TextNode('"Escaped'),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_parse_style_underscore():
    source = "_Some text_"

    expected = [
        SentenceNode(
            [
                StyleNode(
                    "underscore",
                    SentenceNode(
                        [
                            TextNode("Some text"),
                        ]
                    ),
                ),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_parse_style_star():
    source = "*Some text*"

    expected = [
        SentenceNode(
            [
                StyleNode(
                    "star",
                    SentenceNode(
                        [
                            TextNode("Some text"),
                        ]
                    ),
                ),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_parse_style_caret():
    source = "^Some text^"

    expected = [
        SentenceNode(
            [
                StyleNode(
                    "caret",
                    SentenceNode(
                        [
                            TextNode("Some text"),
                        ]
                    ),
                ),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_parse_style_tilde():
    source = "~Some text~"

    expected = [
        SentenceNode(
            [
                StyleNode(
                    "tilde",
                    SentenceNode(
                        [
                            TextNode("Some text"),
                        ]
                    ),
                ),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_style_within_style():
    source = "_*Words with two styles*_"

    expected = [
        SentenceNode(
            [
                StyleNode(
                    "underscore",
                    SentenceNode(
                        [
                            StyleNode(
                                "star",
                                SentenceNode([TextNode("Words with two styles")]),
                            )
                        ]
                    ),
                )
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_paragraph_double_style_cancels_itself():
    source = "__Text__"

    expected = [
        SentenceNode(
            [
                StyleNode("underscore", SentenceNode([])),
                TextNode("Text"),
                StyleNode("underscore", SentenceNode([])),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_text_and_styles():
    source = "Some text _and style_ and *more style* here"

    expected = [
        SentenceNode(
            [
                TextNode("Some text "),
                StyleNode(
                    "underscore",
                    SentenceNode(
                        [
                            TextNode("and style"),
                        ]
                    ),
                ),
                TextNode(" and "),
                StyleNode(
                    "star",
                    SentenceNode(
                        [
                            TextNode("more style"),
                        ]
                    ),
                ),
                TextNode(" here"),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_parse_style_open():
    source = "_Text"

    expected = [
        SentenceNode(
            [
                TextNode("_Text"),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_verbatim():
    source = "`Many different words`"

    expected = [
        SentenceNode(
            [
                VerbatimNode("Many different words"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_verbatim_escaped_backtick():
    source = r"`\``"

    expected = [
        SentenceNode(
            [
                VerbatimNode("`"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_verbatim_style_inside_verbatim():
    source = r"`_Many different words_`"

    expected = [
        SentenceNode(
            [
                VerbatimNode("_Many different words_"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_verbatim_open():
    source = r"`Many different words"

    expected = [
        SentenceNode(
            [
                TextNode("`Many different words"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_verbatim_and_style():
    source = "Some text with `verbatim words` and _styled ones_"

    expected = [
        SentenceNode(
            [
                TextNode("Some text with "),
                VerbatimNode("verbatim words"),
                TextNode(" and "),
                StyleNode(
                    "underscore",
                    SentenceNode(
                        [
                            TextNode("styled ones"),
                        ]
                    ),
                ),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_square_brackets():
    source = "This contains [ and ] and [this]"

    expected = [
        SentenceNode(
            [
                TextNode("This contains [ and ] and [this]"),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_collect_macro_arguments_single_argument():
    source = "(value1)"

    parser = init_parser(source)
    assert parser._collect_macro_args() == "value1"


def test_collect_macro_arguments_multiple_arguments():
    source = "(value1,value2)"

    parser = init_parser(source)
    assert parser._collect_macro_args() == "value1,value2"


def test_collect_macro_arguments_single_argument_with_quotes():
    source = '("value1")'

    parser = init_parser(source)
    assert parser._collect_macro_args() == '"value1"'


def test_collect_macro_arguments_single_argument_with_quotes_and_parenthesis():
    source = '("value1()")'

    parser = init_parser(source)
    assert parser._collect_macro_args() == '"value1()"'


def test_collect_macro_arguments_single_argument_with_parenthesis():
    source = "(value1())"

    parser = init_parser(source)
    assert parser._collect_macro_args() == "value1("


def test_collect_macro_arguments_multiple_argument_with_quotes_and_parenthesis():
    source = '("value1()",value2,value3)'

    parser = init_parser(source)
    assert parser._collect_macro_args() == '"value1()",value2,value3'


def test_collect_macro_arguments_multiple_argument_with_escaped_quotes():
    source = r"(\"value2,value3)"

    parser = init_parser(source)
    assert parser._collect_macro_args() == r"\"value2,value3"


def test_macro():
    source = "[macroname](value1,value2)"

    expected = [
        SentenceNode(
            [
                MacroNode(
                    "macroname",
                    args=["value1", "value2"],
                ),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_incomplete_macro():
    source = "[macroname](value1"

    expected = [
        SentenceNode(
            [
                TextNode(
                    "[macroname](value1",
                ),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_arguments_with_quotes():
    source = '[macroname]("value1,value2")'

    expected = [
        SentenceNode(
            [
                MacroNode(
                    "macroname",
                    args=["value1,value2"],
                ),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_named_arguments():
    source = "[macroname](name,arg1=value1)"

    expected = [
        SentenceNode(
            [
                MacroNode(
                    "macroname",
                    args=["name"],
                    kwargs={"arg1": "value1"},
                ),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_link():
    source = '[link](https://somedomain.org/the/path, "link text")'

    expected = [
        SentenceNode(
            [
                LinkNode("https://somedomain.org/the/path", "link text"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_link_without_text():
    source = '[link]("https://somedomain.org/the/path")'

    expected = [
        SentenceNode(
            [
                LinkNode(
                    "https://somedomain.org/the/path", "https://somedomain.org/the/path"
                ),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_mailto():
    source = "[mailto](info@projectmau.org)"

    expected = [
        SentenceNode(
            [
                LinkNode("mailto:info@projectmau.org", "info@projectmau.org"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_mailto_custom_text():
    source = '[mailto](info@projectmau.org, "my email")'

    expected = [
        SentenceNode(
            [
                LinkNode("mailto:info@projectmau.org", "my email"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_footnote():
    source = "[footnote](notename)"

    footnote_node = FootnoteNode()
    expected = [SentenceNode([footnote_node])]

    parser = runner(source)
    assert parser.nodes == expected
    assert parser.footnotes == {"notename": footnote_node}


def test_macro_reference():
    source = "[reference](solution, value)"

    reference_node = ReferenceNode("solution", "value")
    expected = [SentenceNode([reference_node])]

    parser = runner(source)
    assert parser.nodes == expected
    assert parser.references == {
        ("solution", "value"): reference_node,
    }


def test_single_class():
    source = 'Some text [class]("text with that class", classname)'

    expected = [
        SentenceNode(
            [
                TextNode("Some text "),
                ClassNode(
                    ["classname"],
                    SentenceNode(
                        [
                            TextNode("text with that class"),
                        ]
                    ),
                ),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_multiple_classes():
    source = 'Some text [class]("text with that class", "classname1,classname2")'

    expected = [
        SentenceNode(
            [
                TextNode("Some text "),
                ClassNode(
                    ["classname1", "classname2"],
                    SentenceNode(
                        [
                            TextNode("text with that class"),
                        ]
                    ),
                ),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_parse_class_with_rich_text():
    source = '[class]("Some text with `verbatim words` and _styled ones_", classname)'

    expected = [
        SentenceNode(
            [
                ClassNode(
                    ["classname"],
                    SentenceNode(
                        [
                            TextNode("Some text with "),
                            VerbatimNode("verbatim words"),
                            TextNode(" and "),
                            StyleNode(
                                "underscore", SentenceNode([TextNode("styled ones")])
                            ),
                        ]
                    ),
                ),
            ]
        )
    ]

    assert runner(source).nodes == expected


def test_macro_image():
    source = "[image](/the/path.jpg)"

    expected = [
        SentenceNode(
            [
                ImageNode("/the/path.jpg"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_image_with_alt_text():
    source = '[image](/the/path.jpg,"alt name")'

    expected = [
        SentenceNode(
            [
                ImageNode("/the/path.jpg", alt_text="alt name"),
            ]
        ),
    ]

    assert runner(source).nodes == expected


def test_macro_image_with_width_and_height():
    source = "[image](/the/path.jpg,width=1200,height=600)"

    expected = [
        SentenceNode(
            [
                ImageNode("/the/path.jpg", alt_text=None, width="1200", height="600"),
            ]
        ),
    ]

    assert runner(source).nodes == expected
