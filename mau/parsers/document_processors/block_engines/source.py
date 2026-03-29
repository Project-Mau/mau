from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mau.parsers.document_parser import DocumentParser


from mau.environment.environment import Environment
from mau.nodes.node import Node, NodeInfo
from mau.nodes.node_arguments import NodeArguments
from mau.nodes.source import (
    SourceLineNode,
    SourceMarkerNode,
    SourceNode,
)
from mau.text_buffer import Context
from mau.token import Token


def create_source_line(
    code: list[SourceLineNode],
    line_number: str,
    line_content: str,
    line_context: Context,
    parent: Node,
    marker_node: SourceMarkerNode | None = None,
    highlight_style: str | None = None,
):
    # Prepare the source line
    source_line_node = SourceLineNode(
        line_number,
        line_content=line_content,
        highlight_style=highlight_style,
        info=NodeInfo(context=line_context),
        parent=parent,
    )

    if marker_node:
        source_line_node.marker = marker_node

    code.append(source_line_node)


def parse_source_engine(
    parser: DocumentParser, content: Token, arguments: NodeArguments
) -> Node:
    # Parse a source block in the form
    #
    # [engine=source]
    # ----
    # content
    # ----
    #
    # Source blocks support the following attributes
    #
    # language The language used to highlight the syntax.
    # marker_delimiter=":" The separator used by marker.
    # highlight_prefix="@" The special character to turn on highlight.
    #
    # Since Mau uses Pygments, the attribute language
    # is one of the languages supported by that tool.

    if not content:
        return SourceNode()

    # Get the delimiter for markers
    marker_delimiter = arguments.named_args.pop("marker_delimiter", ":")

    # Get the highlight prefix
    highlight_prefix = arguments.named_args.pop("highlight_marker", "@")

    # Get the default highlight style
    highlight_default_style = arguments.named_args.pop(
        "highlight_default_style", "default"
    )

    style_aliases = parser.environment.get(
        "mau.parser.source_highlight_style_aliases", Environment()
    ).asdict()

    # Get the language
    arguments.set_names(["language"])
    language = arguments.named_args.pop("language", "text")

    # A list of content lines (raw).
    content_lines = content.value.split("\n")

    # A list of code lines (after processing).
    code: list[SourceLineNode] = []

    node = SourceNode(language)

    for number, line_content in enumerate(content_lines, start=1):
        line_number = str(number)

        line_context = content.context.clone()
        line_context.start_line += number - 1
        line_context.end_line = line_context.start_line
        line_context.end_column = line_context.start_column + len(line_content)

        marker: str | None = None
        highlight_style: str | None = None

        if not line_content.endswith(marker_delimiter):
            create_source_line(
                code,
                line_number,
                line_content,
                line_context,
                parent=node,
            )
            continue

        # Split without the final delimiter
        splits = line_content[:-1].split(marker_delimiter)

        if len(splits) < 2:
            # It's a trap! There are no separators left.
            # Just add the line as it is.
            create_source_line(
                code,
                line_number,
                line_content,
                line_context,
                parent=node,
            )
            continue

        # Get the callout and the line
        marker = splits[-1]
        line_content = marker_delimiter.join(splits[:-1])

        if marker.startswith(highlight_prefix):
            highlight_style = marker[1:] or highlight_default_style

            # Replace the highlight style
            # if it is an alias.
            highlight_style = style_aliases.get(highlight_style, highlight_style)

            marker = None

        marker_node: SourceMarkerNode | None = None

        # If there is a marker, change the line
        # context to remove the marker.
        if marker:
            # Take into account the two colons.
            marker_length = len(marker) + 2

            # Calculate the line length.
            line_length = len(line_content)

            # Clone the line context.
            marker_context = line_context.clone()

            # Remove the marker from the end
            # of the line context.
            line_context.end_column -= marker_length

            # Remove the line from the
            # marker context.
            marker_context.start_column += line_length

            marker_node = SourceMarkerNode(
                marker,
                info=NodeInfo(context=marker_context),
            )

        create_source_line(
            code,
            line_number,
            line_content,
            line_context,
            parent=node,
            marker_node=marker_node,
            highlight_style=highlight_style,
        )

    node.content = code
    node.info = NodeInfo(context=content.context)

    return node
