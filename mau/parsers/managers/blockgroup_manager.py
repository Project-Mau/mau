from __future__ import annotations

from collections import defaultdict

from mau.nodes.block import BlockNode
from mau.nodes.include import BlockGroupItemNode, BlockGroupNode
from mau.parsers.base_parser import create_parser_exception


class BlockGroupManager:
    def __init__(self):
        # This dictionary contains the block nodes
        # organised by group.
        self.items: dict[str, dict[str, BlockGroupItemNode]] = defaultdict(dict)

        # type: ignore[arg-type]

        # This list contains the group nodes that
        # will eventually render the group.
        self.groups: list[BlockGroupNode] = []

    def add_block(self, group: str, position: str, node: BlockNode):
        """Add a block to the list of managed blocks."""
        blockgroup = self.items[group]

        # Check if the position in the
        # block is already taken.
        if blockgroup.get(position):
            raise create_parser_exception(
                text=f"Position '{position}' is already taken in group '{group}'.",
                context=node.info.context,
            )

        # Create the blockgroup item.
        blockgroup_item = BlockGroupItemNode(group, position, node)

        # Make sure the block is a child of
        # the blockgroup items.
        node.parent = blockgroup_item

        # Add the blockgroup item to the
        # blockgroup at the requested position.
        blockgroup[position] = blockgroup_item

    def add_group(self, data: BlockGroupNode):
        """Add a group node to the list of
        managed group nodes."""
        self.groups.append(data)

    def process(self):
        # Process all group nodes.
        # For each node, find if the relative
        # group exists and add all the nodes
        # in the group to the group node.

        for group_node in self.groups:
            # Get the referenced group.
            group_name = group_node.name

            # Check if the requested group exists.
            if group_name not in self.items:
                raise create_parser_exception(
                    f"The group '{group_name}' does not exist.",
                    group_node.info.context,
                )

            # Add all blocks that mention this
            # group to the group node.
            group_node.items.update(self.items[group_name])

            # Add each block that mention this
            # group to the group node and add
            # the group as the parent node.
            for position, block_item in self.items[group_name].items():
                block_item.parent = group_node
                group_node.items[position] = block_item
