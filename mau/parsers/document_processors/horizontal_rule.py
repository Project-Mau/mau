from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from mau.nodes.document import HorizontalRuleNode
from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.token import TokenType


def horizontal_rule_processor(parser: DocumentParser):
    # The horizontal rule ---

    # Get the horizontal rule token.
    rule = parser.tm.get_token(TokenType.HORIZONTAL_RULE)

    # Get the stored arguments.
    # Horizontal rules can receive arguments
    # only through the arguments manager.
    arguments = parser.arguments_buffer.pop_or_default()

    # Create the node.
    node = HorizontalRuleNode(
        arguments=NodeArguments(
            **arguments.asdict(),
        ),
        info=NodeInfo(
            context=rule.context,
        ),
    )

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
