from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser

from enum import Enum

from mau.nodes.node import NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.parsers.base_parser import create_parser_exception
from mau.parsers.document_processors.block_engines.default import parse_default_engine
from mau.parsers.document_processors.block_engines.raw import parse_raw_engine
from mau.parsers.document_processors.block_engines.source import parse_source_engine
from mau.text_buffer import Context
from mau.token import Token, TokenType


class EngineType(Enum):
    DEFAULT = "default"
    RAW = "raw"
    SOURCE = "source"


def block_processor(parser: DocumentParser):
    # Parse a block in the form
    #
    # [block_type]
    # ----
    # Content
    # ----
    # Optional secondary content
    #
    # Blocks are delimited by 4 consecutive identical characters.

    # Get the opening delimiter.
    opening_delimiter = parser.tm.get_token(TokenType.BLOCK)

    content: Token | None = None
    if parser.tm.peek_token().type == TokenType.TEXT:
        # Get the content of the block.
        content = parser.tm.get_token(TokenType.TEXT)

    # Get the closing delimiter.
    closing_delimiter = parser.tm.get_token(TokenType.BLOCK)

    # Find the final context.
    context = Context.merge_contexts(
        opening_delimiter.context, closing_delimiter.context
    )

    # Get the stored arguments.
    # Paragraphs can receive arguments
    # only through the arguments manager.
    arguments = parser.arguments_buffer.pop_or_default()

    # Extract classes and convert them into a list
    classes_str = arguments.named_args.pop("classes", "")
    classes = classes_str.split(",") if classes_str else []

    # Extract the engine
    engine_name = arguments.named_args.pop("engine", "default")
    try:
        engine: EngineType = EngineType(engine_name)
    except ValueError as exc:
        raise create_parser_exception(
            f"Engine '{engine_name}' is not available.",
            context=context,
        ) from exc

    match engine:
        # Real engine: decides how the content is processed
        case EngineType.DEFAULT:
            node = parse_default_engine(parser, content, arguments)

        case EngineType.RAW:  # Real engine: decides how the content is processed
            node = parse_raw_engine(parser, content, arguments)

        case EngineType.SOURCE:  # Real engine: decides how the content is processed
            node = parse_source_engine(parser, content, arguments)

    node.classes = classes

    # Extract labels from the buffer and
    # store them in the node data.
    parser.pop_labels(node)

    footnote_name = arguments.named_args.get("footnote")

    if footnote_name:
        parser.footnotes_manager.add_body(footnote_name, node)

        return True

    group_name = arguments.named_args.get("group")
    position = arguments.named_args.get("position")

    node.info = NodeInfo(context=context)
    node.arguments = NodeArguments(**arguments.asdict())

    if group_name and position:
        parser.blockgroup_manager.add_block(group_name, position, node)

        return True

    # Check the stored control
    if control := parser.control_buffer.pop():
        # If control is False, we need to stop
        # processing here and return without
        # saving any node.
        if not control.process(parser.environment):
            return True

    parser._save(node)

    return True
