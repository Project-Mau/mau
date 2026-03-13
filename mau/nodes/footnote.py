from collections.abc import Sequence

from mau.nodes.node import Node, NodeContentMixin, NodeInfo
from mau.nodes.node_arguments import NodeArguments


class FootnoteNode(Node, NodeContentMixin):
    """The content of a footnote."""

    type = "footnote"

    def __init__(
        self,
        # The unique internal name of the
        # referenced footnote content.
        # This name is used to link a
        # footnote macro (mention) with its
        # block (definition).
        name: str,
        # The unique public ID assigned to this footnote
        # (typically a progressive number).
        # This ID can be displayed on the rendered text.
        public_id: str | None = None,
        # The unique ID assigned to this footnote
        # that can be used to create references in
        # the rendered text.
        internal_id: str | None = None,
        content: Sequence[Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeContentMixin.__init__(self, content)

        self.name = name
        self.public_id = public_id
        self.internal_id = internal_id

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.name = self.name
        new_node.public_id = self.public_id
        new_node.internal_id = self.internal_id

        # Recursive deep copies.
        self._deepcopy_content(new_node)

        return new_node
