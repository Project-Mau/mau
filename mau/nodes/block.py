from collections.abc import Mapping, Sequence

from mau.nodes.node import (
    Node,
    NodeArguments,
    NodeContentMixin,
    NodeInfo,
    NodeLabelsMixin,
)


class BlockNode(Node, NodeLabelsMixin, NodeContentMixin):
    """A block.

    This node contains a generic block.

    Arguments:
        classes: a comma-separated list of classes
        engine: the engine used to render this block
        preprocessor: the preprocessor used for this block
    """

    type = "block"

    def __init__(
        self,
        classes: Sequence[str] | None = None,
        content: Sequence[Node] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeContentMixin.__init__(self, content)
        NodeLabelsMixin.__init__(self, labels)

        self.classes = classes or []

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.classes = list(self.classes)

        # Recursive deep copies.
        self._deepcopy_content(new_node)
        self._deepcopy_labels(new_node)

        return new_node
