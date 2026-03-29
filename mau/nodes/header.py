from collections.abc import Mapping

from mau.nodes.node import (
    Node,
    NodeArguments,
    NodeContentMixin,
    NodeInfo,
    NodeLabelsMixin,
)

HEADER_HELP = """
Syntax:

([ARGS])?
(@CONTROL)?
(=)+ HEADER

The header prefix `=` can be repeated multiple times to create a
header on a deeper level.
"""


class HeaderNode(Node, NodeLabelsMixin, NodeContentMixin):
    """A header."""

    type = "header"

    def __init__(
        self,
        level: int,
        # The internal unique ID assigned to this header
        # that can be used to create references in
        # the rendered text.
        internal_id: str | None = None,
        # The unique internal name of the
        # referenced header content.
        # This name is used to link a
        # header macro (mention) with its
        # header (definition).
        name: str | None = None,
        content: list[Node] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        self.level = level
        self.internal_id = internal_id

        # This is a name for this header,
        # used to link it internally.
        # Headers with an name will still
        # receive a programmatic ID.
        # TODO clarify and use correct names.
        self.name = name

        NodeContentMixin.__init__(self, content)
        NodeLabelsMixin.__init__(self, labels)

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.level = self.level
        new_node.internal_id = self.internal_id
        new_node.name = self.name

        # Recursive deep copies.
        self._deepcopy_content(new_node)
        self._deepcopy_labels(new_node)

        return new_node
