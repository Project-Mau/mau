from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import ListItemNode, SentenceNode, TextNode
from mau.nodes.page import ListNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_parse_list_with_one_item():
    source = """
    * This is a list with one element
    """

    assert runner(source).nodes == [
        ListNode(
            False,
            [
                ListItemNode(
                    "1", SentenceNode([TextNode("This is a list with one element")])
                )
            ],
            True,
        )
    ]


def test_parse_list_with_multiple_items():
    source = """
    * Item 1
    * Item 2
    """

    assert runner(source).nodes == [
        ListNode(
            False,
            [
                ListItemNode("1", SentenceNode([TextNode("Item 1")])),
                ListItemNode("1", SentenceNode([TextNode("Item 2")])),
            ],
            True,
        )
    ]


def test_parse_list_with_multiple_levels():
    source = """
    * Item 1
    ** Item 1.1
    * Item 2
    """

    assert runner(source).nodes == [
        ListNode(
            False,
            [
                ListItemNode(
                    "1",
                    SentenceNode(
                        [
                            TextNode("Item 1"),
                            ListNode(
                                False,
                                [
                                    ListItemNode(
                                        "2",
                                        SentenceNode(
                                            [
                                                TextNode("Item 1.1"),
                                            ]
                                        ),
                                    )
                                ],
                                False,
                            ),
                        ]
                    ),
                ),
                ListItemNode("1", SentenceNode([TextNode("Item 2")])),
            ],
            True,
        )
    ]


def test_parse_numbered_list():
    source = """
    # Item 1
    ## Item 1.1
    # Item 2
    """

    assert runner(source).nodes == [
        ListNode(
            True,
            [
                ListItemNode(
                    "1",
                    SentenceNode(
                        [
                            TextNode("Item 1"),
                            ListNode(
                                True,
                                [
                                    ListItemNode(
                                        "2",
                                        SentenceNode(
                                            [
                                                TextNode("Item 1.1"),
                                            ]
                                        ),
                                    )
                                ],
                                False,
                            ),
                        ]
                    ),
                ),
                ListItemNode(
                    "1",
                    SentenceNode(
                        [TextNode("Item 2")],
                    ),
                ),
            ],
            True,
        )
    ]


def test_parse_mixed_list():
    source = """
    * Item 1
    ## Item 1.1
    * Item 2
    """

    assert runner(source).nodes == [
        ListNode(
            False,
            [
                ListItemNode(
                    "1",
                    SentenceNode(
                        [
                            TextNode("Item 1"),
                            ListNode(
                                True,
                                [
                                    ListItemNode(
                                        "2",
                                        SentenceNode(
                                            [
                                                TextNode("Item 1.1"),
                                            ]
                                        ),
                                    )
                                ],
                                False,
                            ),
                        ]
                    ),
                ),
                ListItemNode("1", SentenceNode([TextNode("Item 2")])),
            ],
            True,
        )
    ]


def test_parse_mixed_list_cannot_change_type():
    source1 = """
    * Item 1
    ## Item 1.1
    # Item 2
    """

    source2 = """
    * Item 1
    ## Item 1.1
    * Item 2
    """

    assert runner(source1).nodes == runner(source2).nodes
