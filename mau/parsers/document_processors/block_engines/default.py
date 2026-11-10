from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from mau.nodes.block import BlockNode
from mau.nodes.node import Node
from mau.nodes.node_arguments import NodeArguments
from mau.token import Token


def parse_block_content(
    parser: DocumentParser, content: Token, arguments: NodeArguments
) -> list[Node]:
    # Blocks are isolated unless `isolate=false`.
    isolate = arguments.named_args.get("isolate", "true") != "false"

    # The parsing environment is
    # that of the external parser.
    environment = parser.environment

    # Unpack the token initial position.
    start_line, start_column = content.context.start_position

    # Get the token source.
    source_filename = content.context.source

    content_parser = parser.lex_and_parse(
        text=content.value,
        message_handler=parser.message_handler,
        environment=environment,
        start_line=start_line,
        start_column=start_column,
        source_filename=source_filename,
        isolate=isolate,
    )

    if not isolate:
        # Since the block wasn't isolated, we
        # need to merge the managers created
        # parsing it.
        parser.merge_managers(content_parser)

    return content_parser.nodes


def parse_default_engine(
    parser: DocumentParser, content: Token | None, arguments: NodeArguments
) -> BlockNode:
    node = BlockNode()

    if not content:
        return node

    # Parse the content of the block.
    nodes = parse_block_content(parser, content, arguments)

    # Assign the block as parent
    # of all nodes directly
    # contained in it.
    for i in nodes:
        i.parent = node

    # Assign the nodes to the block.
    node.content = nodes

    return node
