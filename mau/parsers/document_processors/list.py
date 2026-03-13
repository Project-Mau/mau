from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from mau.nodes.list import ListItemNode, ListNode
from mau.nodes.node import Node, NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.parsers.base_parser import create_parser_exception
from mau.text_buffer import Context
from mau.token import Token, TokenType


def _process_list_nodes(parser: DocumentParser, parent: Node):
    # This parses all items of a list

    # Parse the header.
    header = parser.tm.get_token(TokenType.LIST)

    # Get the text of the item.
    text = parser.tm.get_token(TokenType.TEXT)

    # Parse the text of the item.
    content = parser._parse_text(text.value, context=text.context, parent=parent)

    # Compute the level of the item
    level = len(header.value)

    # Find the final context.
    context = Context.merge_contexts(header.context, content[-1].info.context)

    nodes: list[Node] = []
    nodes.append(
        ListItemNode(
            level, content=content, info=NodeInfo(context=context), parent=parent
        )
    )

    while parser.tm.peek_token() not in [
        Token.generate(TokenType.EOF),
        Token.generate(TokenType.EOL),
    ]:
        if not parser.tm.peek_token_is(TokenType.LIST):
            # Something fishy happened in the source text.
            # The next token is not the EOL or EOF,
            # so we expect a new list item, but the
            # token is not LIST.
            raise create_parser_exception(
                "Wrong syntax encountered while processing the list.",
                context=parser.tm.peek_token().context,
            )

        if len(parser.tm.peek_token().value) == level:
            # The new item is on the same level

            # Get the header
            header = parser.tm.get_token()

            # Get the text of the item.
            text = parser.tm.get_token(TokenType.TEXT)

            # Parse the text of the item.
            content = parser._parse_text(
                text.value, context=text.context, parent=parent
            )

            # Compute the level of the item
            level = len(header.value)

            # Find the final context.
            context = Context.merge_contexts(header.context, content[-1].info.context)

            nodes.append(
                ListItemNode(
                    level,
                    content=content,
                    parent=parent,
                    info=NodeInfo(context=context),
                )
            )

        elif len(parser.tm.peek_token().value) > level:
            # The new item is on a deeper level

            # Peek the header
            header = parser.tm.peek_token(TokenType.LIST)
            ordered = header.value[0] == "#"

            # Parse all the items at this level or higher.
            subnodes = _process_list_nodes(parser, parent)

            # Find the final context.
            context = Context.merge_contexts(header.context, subnodes[-1].info.context)

            nodes.append(
                ListNode(
                    ordered=ordered,
                    content=subnodes,
                    parent=parent,
                    info=NodeInfo(context=context),
                )
            )
        else:
            break

    return nodes


def list_processor(parser: DocumentParser):
    # Parse a list.
    # Lists can be ordered (using numbers)
    #
    # * One item
    # * Another item
    #
    # or unordered (using bullets)
    #
    # # Item 1
    # # Item 2
    #
    # The number of headers increases
    # the depth of each item
    #
    # # Item 1
    # ## Sub-Item 1.1
    #
    # Spaces before and after the header are ignored.
    # So the previous list can be also written
    #
    # # Item 1
    #   ## Sub-Item 1.1
    #
    # Ordered and unordered lists can be mixed.
    #
    # * One item
    # ## Sub Item 1
    # ## Sub Item 2
    #

    # Get the header and decide if it's a numbered or unnumbered list
    header = parser.tm.peek_token(TokenType.LIST)
    ordered = header.value[0] == "#"

    node = ListNode(
        ordered=ordered,
        main_node=True,
    )

    # Parse all the following items
    nodes = _process_list_nodes(parser, parent=node)

    # Get the stored arguments.
    # Lists can receive arguments
    # only through the arguments manager.
    arguments = parser.arguments_buffer.pop_or_default()

    # Check if the list has a forced start.
    if (start := arguments.named_args.get("start", 1)) == "auto":
        start = parser.latest_ordered_list_index
        parser.latest_ordered_list_index += len(nodes)
    else:
        start = int(start)
        parser.latest_ordered_list_index = len(nodes) + start

    # Find the final context.
    context = Context.merge_contexts(nodes[0].info.context, nodes[-1].info.context)

    node.start = start
    node.content = nodes
    node.info = NodeInfo(context=context)
    node.arguments = NodeArguments(**arguments.asdict())

    # Extract labels from the buffer and
    # store them in the node data.
    parser.pop_labels(node)

    # Check the stored control
    if control := parser.control_buffer.pop():
        # If control is False, we need to stop
        # processing here and return without
        # saving any node.
        if not control.process(parser.environment):
            return True

    parser._save(node)

    return True
