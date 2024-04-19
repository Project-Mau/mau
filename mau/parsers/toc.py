import hashlib
import re

from mau.nodes.toc import TocEntryNode, TocNode


class TocManager:
    def __init__(self, parser):
        # This list contains the headers
        # found parsing a document
        self.headers = []

        # This list contains all the ToC entries
        # that will be shown by a toc command.
        self.tocnodes = []

        # This is the list of ::toc commands
        # that need to be updated once the ToC
        # has been processed
        self.command_nodes = []

        # This is the parser that contains the manager
        self.parser = parser

    def add_header_node(self, node):
        self.headers.append(node)

    def create_toc_node(self, subtype, args, kwargs, tags):
        # This creates an empty TocNode
        # that will be stored in the parser
        # and in the command_nodes list.
        # The method process_footnotes will
        # eventually update all these nodes
        # with the right entries.
        node = TocNode(
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )

        self.command_nodes.append(node)
        self.parser.save(node)

    def process_toc(self):
        toc = TocNode(children=create_toc(self.headers))

        for node in self.command_nodes:
            node.children = create_toc(
                self.headers, exclude_tag=node.kwargs.get("exclude_tag")
            )

        return toc

    def update(self, other):
        self.headers.extend(other.headers)
        self.command_nodes.extend(other.command_nodes)


def create_toc(headers, exclude_tag=None):
    # Create the TOC from the list of headers.

    nodes = []
    latest_by_level = {}

    for header_node in headers:
        # This is the current node
        node = TocEntryNode(
            value=header_node.value,
            anchor=header_node.anchor,
            tags=header_node.tags,
        )
        level = int(header_node.level)

        # This collects the latest node added with a given level
        latest_by_level[level] = node

        try:
            # Simplest case, add it to the latest one
            # with a level just 1 step lower
            latest_by_level[level - 1].children.append(node)
        except KeyError:
            # Find all the latest ones added with a level lower than this
            latest = [latest_by_level.get(i, None) for i in range(1, level)]

            # Get the children list of each one, plus nodes for the root
            children = [nodes] + [i.children for i in latest if i is not None]

            # Get the nearest one and append to that
            children[-1].append(node)

    if exclude_tag:
        nodes = exclude_children(nodes, exclude_tag)

    return nodes


def header_anchor(text, level):
    """
    Return a sanitised anchor for a header.
    """

    # Everything lowercase
    sanitised_text = text.lower()

    # Get only letters, numbers, dashes, spaces, and dots
    sanitised_text = "".join(re.findall("[a-z0-9-\\. ]+", sanitised_text))

    # Remove multiple spaces
    sanitised_text = "-".join(sanitised_text.split())

    hashed_value = hashlib.md5(f"{level} {text}".encode("utf-8")).hexdigest()[:4]

    return f"{sanitised_text}-{hashed_value}"


def exclude_children(children, exclude_tag):
    valid_children = [i for i in children if exclude_tag not in i.tags]

    for entry in valid_children:
        entry.children = exclude_children(entry.children, exclude_tag)

    return valid_children
