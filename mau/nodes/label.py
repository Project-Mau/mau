from __future__ import annotations

from collections.abc import Sequence

from mau.nodes.node import Node, NodeInfo, WrapperNode
from mau.nodes.node_arguments import NodeArguments


class LabelNode(WrapperNode):
    """A label attached to another node.

    This wraps the label's inline content and
    carries the role (e.g. "title", "cite").
    """

    type = "label"

    def __init__(
        self,
        role: str,
        content: Sequence[Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info, content=content)

        self.role = role

    def deepcopy(self, parent=None):  # pragma: no cover
        new_node = super().deepcopy(parent)
        new_node.role = self.role
        return new_node

    @property
    def custom_template_fields(self) -> dict:
        return {
            "role": self.role,
        }
