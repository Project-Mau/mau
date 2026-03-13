import pytest

from mau.message import MauException, MauMessageType
from mau.nodes.block import BlockNode
from mau.nodes.include import BlockGroupItemNode, BlockGroupNode
from mau.parsers.managers.blockgroup_manager import (
    BlockGroupManager,
)
from mau.test_helpers import compare_nodes


def test_blockgroup_manager():
    bgm = BlockGroupManager()

    block_node1 = BlockNode()
    block_node2 = BlockNode()
    block_node3 = BlockNode()

    bgm.add_block("group1", "position1", block_node1)
    bgm.add_block("group1", "position2", block_node2)
    bgm.add_block("group2", "position1", block_node3)

    assert bgm.items["group1"]["position1"].block == block_node1
    assert bgm.items["group1"]["position2"].block == block_node2
    assert bgm.items["group2"]["position1"].block == block_node3


def test_blockgroup_manager_same_position():
    bgm = BlockGroupManager()

    block_node1 = BlockNode()
    block_node2 = BlockNode()

    bgm.add_block("group1", "position1", block_node1)

    with pytest.raises(MauException) as exc:
        bgm.add_block("group1", "position1", block_node2)

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert (
        exc.value.message.text
        == "Position 'position1' is already taken in group 'group1'."
    )


def test_blockgroup_manager_add_group_node():
    bgm = BlockGroupManager()

    group_node = BlockGroupNode("somename")

    bgm.add_group(group_node)

    assert bgm.groups == [group_node]


def test_blockgroup_manager_process():
    bgm = BlockGroupManager()

    block_node1 = BlockNode()
    block_node2 = BlockNode()
    block_node3 = BlockNode()

    bgm.add_block("group1", "position1", block_node1)
    bgm.add_block("group1", "position2", block_node2)
    bgm.add_block("group2", "position1", block_node3)

    group_node = BlockGroupNode("group1")

    blockgroup_item_node1 = BlockGroupItemNode(
        "group1",
        "position1",
        block_node1,
        parent=group_node,
    )
    blockgroup_item_node2 = BlockGroupItemNode(
        "group1",
        "position2",
        block_node2,
        parent=group_node,
    )

    bgm.add_group(group_node)

    expected_node = BlockGroupNode(
        "group1",
        items={
            "position1": blockgroup_item_node1,
            "position2": blockgroup_item_node2,
        },
    )

    bgm.process()

    compare_nodes(group_node, expected_node)


def test_blockgroup_manager_process_group_does_not_exist():
    bgm = BlockGroupManager()

    group_node = BlockGroupNode("group1")

    bgm.add_group(group_node)

    with pytest.raises(MauException) as exc:
        bgm.process()

    assert exc.value.message.type == MauMessageType.ERROR_PARSER
    assert exc.value.message.text == "The group 'group1' does not exist."
