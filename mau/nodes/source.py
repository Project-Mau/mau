from collections.abc import Mapping, Sequence

from mau.nodes.node import Node, NodeInfo, NodeLabelsMixin, ValueNode
from mau.nodes.node_arguments import NodeArguments


class SourceMarkerNode(ValueNode):
    # This is a marker near a source code line

    type = "source-marker"


class SourceLineNode(Node):
    """A line of verbatim text or source code."""

    type = "source-line"

    def __init__(
        self,
        line_number: str,
        line_content: str,
        highlight_style: str | None = None,
        marker: SourceMarkerNode | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        self.line_number = line_number
        self.line_content = line_content
        self.highlight_style = highlight_style
        self.marker = marker

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.line_number = self.line_number
        new_node.line_content = self.line_content
        new_node.highlight_style = self.highlight_style
        new_node.marker = self.marker.deepcopy(parent=new_node) if self.marker else None

        return new_node


class SourceNode(Node, NodeLabelsMixin):
    """A block of verbatim text or source code.

    This node contains verbatim text or source code.
    """

    type = "source"

    def __init__(
        self,
        language: str | None = None,
        classes: Sequence[str] | None = None,
        content: Sequence[SourceLineNode] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        NodeLabelsMixin.__init__(self, labels)

        self.language = language
        self.classes = classes or []
        self.content = content or []

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.language = self.language
        new_node.classes = list(self.classes)
        new_node.content = [child.deepcopy(parent=new_node) for child in self.content]

        # Recursive deep copies.
        self._deepcopy_labels(new_node)

        return new_node
