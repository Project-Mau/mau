from collections.abc import Mapping

from mau.nodes.node import Node, NodeInfo, NodeLabelsMixin, WrapperNode
from mau.nodes.node_arguments import NodeArguments

HORIZONTAL_RULE_HELP = """
Syntax:

([ARGS])?
---

The horizontal rule marks a separation between text sections
in the same document.
"""


class HorizontalRuleNode(Node, NodeLabelsMixin):
    """A horizontal rule."""

    type = "horizontal-rule"

    def __init__(
        self,
        labels: Mapping[str, list[Node]] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeLabelsMixin.__init__(self, labels)

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Recursive deep copies.
        self._deepcopy_labels(new_node)

        return new_node


class DocumentNode(WrapperNode):
    """A document.

    This node represents the full document.

    Arguments:
        content: the content of the document
    """

    type = "document"
