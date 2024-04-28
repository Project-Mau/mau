import pytest
from mau.errors import MauErrorException
from mau.lexers.main_lexer import MainLexer
from mau.nodes.block import BlockGroupNode, BlockNode
from mau.nodes.inline import TextNode
from mau.nodes.paragraph import ParagraphNode
from mau.parsers.main_parser import MainParser

from tests.helpers import init_parser_factory, parser_runner_factory

init_parser = init_parser_factory(MainLexer, MainParser)

runner = parser_runner_factory(MainLexer, MainParser)


def test_engine_group():
    source = """
    [*sometype1, engine=group, group=somegroup, position=left]
    ----
    Block 1
    ----
    
    [*sometype2, engine=group, group=somegroup, position=right]
    ----
    Block 2
    ----
    """

    par = runner(source)

    assert par.nodes == []

    assert par.grouped_blocks == {
        "somegroup": {
            "left": BlockNode(
                subtype="sometype1",
                children=[
                    ParagraphNode(
                        children=[
                            TextNode("Block 1"),
                        ]
                    ),
                ],
                secondary_children=[],
                classes=[],
                title=None,
                engine="group",
                preprocessor="none",
                args=[],
                kwargs={},
            ),
            "right": BlockNode(
                subtype="sometype2",
                children=[
                    ParagraphNode(
                        children=[
                            TextNode("Block 2"),
                        ]
                    ),
                ],
                secondary_children=[],
                classes=[],
                title=None,
                engine="group",
                preprocessor="none",
                args=[],
                kwargs={},
            ),
        }
    }


def test_engine_group_duplicate_position():
    source = """
    [*sometype1, engine=group, group=somegroup, position=left]
    ----
    Block 1
    ----
    
    [*sometype2, engine=group, group=somegroup, position=left]
    ----
    Block 2
    ----
    """

    with pytest.raises(MauErrorException):
        runner(source)


def test_engine_group_command_group():
    source = """
    [*sometype1, engine=group, group=somegroup, position=left]
    ----
    Block 1
    ----
    
    [*sometype2, engine=group, group=somegroup, position=right]
    ----
    Block 2
    ----

    ::blockgroup:somegroup
    """

    par = runner(source)

    assert par.nodes == [
        BlockGroupNode(
            group_name="somegroup",
            subtype=None,
            children=[],
            group={
                "left": BlockNode(
                    subtype="sometype1",
                    children=[
                        ParagraphNode(
                            children=[
                                TextNode("Block 1"),
                            ]
                        ),
                    ],
                    secondary_children=[],
                    classes=[],
                    title=None,
                    engine="group",
                    preprocessor="none",
                    args=[],
                    kwargs={},
                ),
                "right": BlockNode(
                    subtype="sometype2",
                    children=[
                        ParagraphNode(
                            children=[
                                TextNode("Block 2"),
                            ]
                        ),
                    ],
                    secondary_children=[],
                    classes=[],
                    title=None,
                    engine="group",
                    preprocessor="none",
                    args=[],
                    kwargs={},
                ),
            },
            title=None,
            args=[],
            kwargs={},
        )
    ]

    assert par.grouped_blocks == {}

    block_group = par.nodes[0]
    block_left = block_group.group["left"]
    block_right = block_group.group["right"]

    assert block_left.parent == block_group
    assert block_left.parent_position == "left"

    assert block_right.parent == block_group
    assert block_right.parent_position == "right"


def test_engine_group_command_group_invalid_group():
    source = """
    ::blockgroup:somegroup
    """

    with pytest.raises(MauErrorException):
        runner(source)
