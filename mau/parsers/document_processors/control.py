from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from mau.parsers.buffers.control_buffer import Control
from mau.parsers.condition_parser import (
    process_condition_with_variables,
)
from mau.text_buffer import Context
from mau.token import TokenType


def control_processor(parser: DocumentParser):
    # Parse control instructions in the form
    #
    # @OPERATOR CONDITION

    # Parse the mandatory @
    prefix_token = parser.tm.get_token(TokenType.CONTROL, "@")

    # Get the operator
    operator = parser.tm.get_token(TokenType.TEXT).value

    # Get the condition
    condition_token = parser.tm.get_token(TokenType.TEXT)

    condition_parser = process_condition_with_variables(
        condition_token, parser.message_handler, parser.environment
    )

    # At the moment we support only one condition.
    condition_node = condition_parser.condition_node

    # Find the final context.
    context = Context.merge_contexts(prefix_token.context, condition_token.context)

    control = Control(
        operator,
        condition_node.variable,
        condition_node.comparison,
        condition_node.value,
        context,
    )

    parser.control_buffer.push(control)

    return True
