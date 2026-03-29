from __future__ import annotations

from mau.nodes.block import BlockNode
from mau.nodes.footnote import FootnoteNode
from mau.nodes.include import FootnotesItemNode, FootnotesNode
from mau.nodes.macro import (
    MacroFootnoteNode,
)
from mau.parsers.base_parser import create_parser_exception


def default_footnote_unique_id(
    footnote: FootnoteNode,
) -> str:  # pragma: no cover
    """
    Return a unique ID for a footnote.
    """

    return footnote.name


class FootnotesManager:
    """This manager collects footnote macros and
    footnote definitions (bodies). When the manager
    process is run, footnote nodes are created from
    bodies, assigned unique IDs, and linked to the
    macros that reference them. Footnote list nodes
    are also populated with the complete set of
    footnotes.
    """

    def __init__(self, footnote_unique_id_function=None):
        # This dictionary contains the footnotes created
        # when processing macros and definitions.
        self.footnotes_dict: dict[str, FootnoteNode] = {}

        # This dictionary contains the footnotes created
        # through macros.
        self.footnote_macros: list[MacroFootnoteNode] = []

        # This dictionary contains the body of each footnote
        # created through blocks.
        self.bodies: dict[str, BlockNode] = {}

        # The list of footnote lists created through includes.
        self.footnotes_list_nodes: list[FootnotesNode] = []

        self.footnote_unique_id_function = (
            footnote_unique_id_function or default_footnote_unique_id
        )

    def add_footnote_macros(self, footnote_macros: list[MacroFootnoteNode]):
        """Add a list of footnote macros to the list
        of managed footnote macros."""
        self.footnote_macros.extend(footnote_macros)

    def add_body(self, name: str, data: BlockNode):
        """Add the content of a footnote to
        the list of contents."""
        if name in self.bodies:
            raise create_parser_exception(
                text=f"Footnote '{name}' has been already defined.",
                context=data.info.context,
            )

        self.bodies[name] = data

    def add_footnotes_list(self, data: FootnotesNode):
        """Add a footnotes list node to
        the list of managed nodes."""
        self.footnotes_list_nodes.append(data)

    def update(self, other: FootnotesManager):
        """Update footnotes, data, and footnotes nodes
        with those contained in another
        Footnotes Manager."""
        self.footnote_macros.extend(other.footnote_macros)
        self.bodies.update(other.bodies)
        self.footnotes_list_nodes.extend(other.footnotes_list_nodes)

    def process(self):
        # Find all footnote names that have been
        # mentioned in macros.
        # mentioned_footnote_names = set([macro.name for macro in self.footnote_macros])

        # Find all footnote names that have been
        # used in footnote blocks.
        # defined_footnote_names = set(self.bodies.keys())

        # Process all bodies. For each body
        # create a footnote, calculate
        # the public and explicit IDs, then
        # macros to it.
        for number, (name, body) in enumerate(self.bodies.items(), start=1):
            # Create a new footnote.
            footnote = FootnoteNode(
                name=name,
                public_id=str(number),
            )

            footnote.content = [node.deepcopy(parent=footnote) for node in body.content]

            # Create the internal ID.
            footnote.internal_id = self.footnote_unique_id_function(footnote)

            # Add the footnote to the list of
            # all footnotes.
            self.footnotes_dict[name] = footnote

        # For each macro, find the footnote it
        # mentions in the list of footnotes
        # and link the macro to it.
        for footnote_macro in self.footnote_macros:
            try:
                footnote_macro.footnote = self.footnotes_dict[footnote_macro.name]
            except KeyError as exc:
                raise create_parser_exception(
                    text=f"Footnote '{footnote_macro.name}' has not been defined.",
                    context=footnote_macro.info.context,
                ) from exc

        # For each footnotes list, add the
        # list of all known footnotes to it.
        # Each footnote in the list is wrapped by
        # a FootnotesItemNode.
        for footnotes_list_node in self.footnotes_list_nodes:
            footnotes_list_node.footnotes = [
                FootnotesItemNode(footnote=footnote, parent=footnotes_list_node)
                for footnote in self.footnotes_dict.values()
            ]
