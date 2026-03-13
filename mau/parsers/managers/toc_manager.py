from __future__ import annotations

import hashlib
import re

from mau.nodes.header import HeaderNode
from mau.nodes.include import (
    TocItemNode,
    TocNode,
)
from mau.nodes.node import Node, NodeContentMixin, ValueNode


def extract_text(nodes):
    """Recursively extract plain text from content nodes."""
    parts = []
    for node in nodes:
        if isinstance(node, ValueNode):
            parts.append(node.value)
        elif isinstance(node, NodeContentMixin):
            parts.append(extract_text(node.content))
    return "".join(parts)


def default_header_internal_id(
    data: HeaderNode,
) -> str:  # pragma: no cover
    """
    Return a unique ID for a header.
    """

    # Get the text of the header from content nodes.
    text = extract_text(data.content)

    # Everything lowercase.
    sanitised_text = text.lower()

    # Get only letters, numbers, dashes, spaces, and dots.
    sanitised_text = "".join(re.findall("[a-z0-9-\\. ]+", sanitised_text))

    # Replace spaces and underscores with dashes.
    sanitised_text = re.sub(r"[\ _]+", "-", sanitised_text)

    # Find the header level.
    level = data.level

    # Calculate a hash.
    # Using the hash means that headers internal ids
    # will clash only if two headers have the same
    # level and the same content.
    # We could use the Python object ID, of course,
    # but this would result in a different internal
    # ID every time Mau runs, which is not acceptable
    # for permanent links.
    # Should there be a clash, the internal_id can
    # be set as an argument to the header.
    # So, a clash is not impossible, but this strategy
    # looks like an acceptable compromise.
    hashed_value = hashlib.md5(f"{level} {text}".encode("utf-8")).hexdigest()[:4]

    return f"{sanitised_text}-{hashed_value}"


def add_nodes_under_level(
    level: int,
    nodes: list[HeaderNode],
    index: int,
    output: list[TocItemNode],
    parent: Node,
) -> int:
    # This recursive function transforms a list
    # of nodes into a hierarchy.

    # In this iteration, make sure we don't go
    # past the given number of nodes.
    while index < len(nodes):
        # If the first node is at a higher or
        # equal level than the current one
        # stop the recursion.
        if nodes[index].level <= level:
            return index

        # Add the first node.
        node = TocItemNode(nodes[index], parent=parent)
        output.append(node)

        # Now perform the recursion on the
        # remaining nodes, adding the
        # children of the node that was
        # just added.
        index = add_nodes_under_level(
            level=nodes[index].level,
            nodes=nodes,
            index=index + 1,
            output=node.entries,
            parent=parent,
        )

    # There are no more nodes to process.
    # if not nodes:
    return index


class TocManager:
    """This manager collects headers and TOC nodes.
    When the manager process is run, all headers
    are given a unique ID (if not already initialised),
    Headers are then reshaped into a hierarchy,
    according to their level and position in the list,
    and both plain and hierarchical headers are added to
    each TOC node.
    """

    def __init__(self, header_internal_id_function=None):
        # This list contains the headers
        # found parsing a document
        self.headers: list[HeaderNode] = []

        # This is the list of toc nodes
        # that need to be updated once the ToC
        # has been processed
        self.toc_nodes: list[TocNode] = []

        self.header_internal_id_function = (
            header_internal_id_function or default_header_internal_id
        )

        self.nested_headers: list[TocItemNode] = []

    def add_header(self, data: HeaderNode):
        """Add a single header to the list
        of managed headers."""
        self.headers.append(data)

    def add_toc_node(self, data: TocNode):
        """Add a single TOC node to the list
        of managed TOC nodes."""
        self.toc_nodes.append(data)

    def update(self, other: TocManager):
        """Update the headers and toc nodes
        with those contained in another
        TOC Manager."""
        self.headers.extend(other.headers)
        self.toc_nodes.extend(other.toc_nodes)

    def process(self):
        if not self.headers:
            return

        self.nested_headers = []

        # Check that all headers have a
        # unique internal ID. If not, create it.
        for header in self.headers:
            if header.internal_id is not None:
                continue

            # Create the unique internal ID.
            internal_id = self.header_internal_id_function(header)
            header.internal_id = internal_id

        # Header parent (the document)
        header_parent = self.headers[0].parent

        # Create the nodes hierarchy.
        # This is done to expose a hierarchy
        # of nodes that have the document as
        # a parent, so that the document
        # can expose a TOC.
        add_nodes_under_level(
            0,
            self.headers,
            0,
            self.nested_headers,
            parent=header_parent,
        )

        # Store the plain and hierarchical nodes
        # inside each TOC node.
        for toc_node in self.toc_nodes:
            # Each toc node receives a new
            # set of nested header because they
            # need to be children of the
            # toc node and not of the document.
            nested_headers: list[TocItemNode] = []

            # Create the nodes hierarchy
            # using the toc node as parent.
            add_nodes_under_level(
                0,
                self.headers,
                0,
                nested_headers,
                parent=toc_node,
            )

            toc_node.nested_entries = nested_headers
            toc_node.plain_entries = [h.deepcopy(parent=toc_node) for h in self.headers]
