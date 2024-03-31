from mau.lexers.main_lexer import MainLexer
from mau.nodes.inline import TextNode
from mau.nodes.lists import ListItemNode, ListNode
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
            ordered=False,
            main_node=True,
            children=[
                ListItemNode(
                    level="1", children=[TextNode("This is a list with one element")]
                )
            ],
        )
    ]


def test_parse_list_with_multiple_items():
    source = """
    * Item 1
    * Item 2
    """

    assert runner(source).nodes == [
        ListNode(
            ordered=False,
            main_node=True,
            children=[
                ListItemNode(level="1", children=[TextNode("Item 1")]),
                ListItemNode(level="1", children=[TextNode("Item 2")]),
            ],
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
            ordered=False,
            main_node=True,
            children=[
                ListItemNode(
                    level="1",
                    children=[
                        TextNode("Item 1"),
                        ListNode(
                            ordered=False,
                            main_node=False,
                            children=[
                                ListItemNode(
                                    level="2",
                                    children=[
                                        TextNode("Item 1.1"),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
                ListItemNode(level="1", children=[TextNode("Item 2")]),
            ],
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
            ordered=True,
            main_node=True,
            children=[
                ListItemNode(
                    level="1",
                    children=[
                        TextNode("Item 1"),
                        ListNode(
                            ordered=True,
                            main_node=False,
                            children=[
                                ListItemNode(
                                    level="2",
                                    children=[
                                        TextNode("Item 1.1"),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 2")],
                ),
            ],
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
            ordered=False,
            main_node=True,
            children=[
                ListItemNode(
                    level="1",
                    children=[
                        TextNode("Item 1"),
                        ListNode(
                            ordered=True,
                            main_node=False,
                            children=[
                                ListItemNode(
                                    level="2",
                                    children=[
                                        TextNode("Item 1.1"),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
                ListItemNode(level="1", children=[TextNode("Item 2")]),
            ],
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


def test_parse_numbered_list_continue():
    source = """
    # Item 1
    # Item 2

    [start=auto]
    # Item 3
    # Item 4
    """

    assert runner(source).nodes == [
        ListNode(
            ordered=True,
            main_node=True,
            start=1,
            children=[
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 1")],
                ),
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 2")],
                ),
            ],
        ),
        ListNode(
            ordered=True,
            main_node=True,
            start=3,
            children=[
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 3")],
                ),
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 4")],
                ),
            ],
            kwargs={},
        ),
    ]


def test_parse_numbered_list_continue_after_forced():
    source = """
    # Item 1
    # Item 2

    [start=20]
    # Item 20
    # Item 21

    [start=auto]
    # Item 22
    # Item 23
    """

    assert runner(source).nodes == [
        ListNode(
            ordered=True,
            main_node=True,
            start=1,
            children=[
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 1")],
                ),
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 2")],
                ),
            ],
        ),
        ListNode(
            ordered=True,
            main_node=True,
            start=20,
            children=[
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 20")],
                ),
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 21")],
                ),
            ],
            kwargs={},
        ),
        ListNode(
            ordered=True,
            main_node=True,
            start=22,
            children=[
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 22")],
                ),
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 23")],
                ),
            ],
            kwargs={},
        ),
    ]


def test_parse_numbered_list_do_not_continue():
    source = """
    # Item 1
    # Item 2

    # Item 3
    # Item 4
    """

    assert runner(source).nodes == [
        ListNode(
            ordered=True,
            main_node=True,
            children=[
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 1")],
                ),
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 2")],
                ),
            ],
        ),
        ListNode(
            ordered=True,
            main_node=True,
            children=[
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 3")],
                ),
                ListItemNode(
                    level="1",
                    children=[TextNode("Item 4")],
                ),
            ],
        ),
    ]


def test_parse_list_with_subtype():
    source = """
    [*type1]
    * This is a list with one element
    """

    assert runner(source).nodes == [
        ListNode(
            ordered=False,
            main_node=True,
            children=[
                ListItemNode(
                    level="1", children=[TextNode("This is a list with one element")]
                )
            ],
            subtype="type1",
        )
    ]
