from collections.abc import Mapping, Sequence

from mau.nodes.node import (
    Node,
    NodeArguments,
    NodeContentMixin,
    NodeInfo,
    NodeLabelsMixin,
)


class ParagraphLineNode(Node, NodeContentMixin, NodeLabelsMixin):
    """
    This node represents the content of a line of a paragraph.
    """

    type = "paragraph-line"

    def __init__(
        self,
        content: Sequence[Node] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeContentMixin.__init__(self, content)
        NodeLabelsMixin.__init__(self, labels)

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Recursive deep copies.
        self._deepcopy_content(new_node)
        self._deepcopy_labels(new_node)
        return new_node


class ParagraphNode(Node, NodeContentMixin, NodeLabelsMixin):
    """A non-recursive container node.

    This node represents the content of a paragraph in a document.
    Its content is a list of lines (ParagraphLineNode)
    """

    type = "paragraph"

    def __init__(
        self,
        content: Sequence[ParagraphLineNode] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeContentMixin.__init__(self, content)
        NodeLabelsMixin.__init__(self, labels)

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Recursive deep copies.
        self._deepcopy_content(new_node)
        self._deepcopy_labels(new_node)

        return new_node
