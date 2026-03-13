from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from mau.nodes.node import Node, NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.raw import RawLineNode, RawNode
from mau.token import Token


def parse_raw_engine(
    parser: DocumentParser, content: Token | None, arguments: NodeArguments
) -> Node:
    # Engine "raw" doesn't process the content,
    # so we just pass it untouched in the form of
    # a RawNode per line.

    if not content:
        return RawNode()

    # A list of content lines (raw).
    content_lines = content.value.split("\n")

    # A list of raw content lines.
    raw_lines: list[RawLineNode] = []

    node = RawNode()

    for number, line_content in enumerate(content_lines, start=1):
        line_context = content.context.clone()
        line_context.start_line += number - 1
        line_context.end_line = line_context.start_line
        line_context.end_column = line_context.start_column + len(line_content)

        raw_lines.append(
            RawLineNode(
                line_content,
                info=NodeInfo(context=line_context),
                parent=node,
            )
        )

    # Assign the nodes to the block.
    node.content = raw_lines

    return node
