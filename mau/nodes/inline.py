from collections.abc import Sequence

from mau.nodes.node import Node, NodeContentMixin, NodeInfo, ValueNode
from mau.nodes.node_arguments import NodeArguments


class WordNode(ValueNode):
    """This is a single word, it's used internally
    and eventually packed together with others into
    a TextNode
    """

    type = "word"


class TextNode(ValueNode):
    """This contains plain text and is created
    as a collation of multiple WordNode objects
    """

    type = "text"


class VerbatimNode(ValueNode):
    """This node contains verbatim text."""

    type = "verbatim"


class StyleNode(Node, NodeContentMixin):
    """Describes the style applied to a node."""

    type = "style"

    def __init__(
        self,
        style: str,
        content: Sequence[Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeContentMixin.__init__(self, content)

        self.style = style

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.style = self.style

        # Recursive deep copies.
        self._deepcopy_content(new_node)

        return new_node

    @property
    def custom_template_fields(self) -> dict:
        return {
            "style": self.style,
        }
