from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from mau.parsers.arguments_parser import (
    process_arguments_with_variables,
)
from mau.token import TokenType


def arguments_processor(parser: DocumentParser):
    # Parse arguments in the form
    # [unnamed1, unnamed2, ..., named1=value1, named2=value2, ...]

    # Check that the token is the opening square bracket.
    parser.tm.get_token(TokenType.ARGUMENTS, "[")

    # Get the text token between brackets.
    arguments_token = parser.tm.get_token(TokenType.TEXT)

    # Check that the token is the closing square bracket.
    parser.tm.get_token(TokenType.LITERAL, "]")

    arguments_parser = process_arguments_with_variables(
        arguments_token, parser.message_handler, parser.environment
    )

    # Store the arguments.
    parser.arguments_buffer.push(arguments_parser.arguments)

    return True
