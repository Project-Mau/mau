from collections.abc import Mapping, Sequence

from mau.nodes.node import (
    Node,
    NodeArguments,
    NodeContentMixin,
    NodeInfo,
    NodeLabelsMixin,
    WrapperNode,
)

LIST_HELP = """
Syntax:

([URI+, ARGS])?
(*+|#+) TEXT

The list prefix `*` or `#` creates a list item. The prefix can be
specified multiple times to nest items, e.g.

* Item 1
** Item 1.1
* Item2

The symbol `*` creates an unordered list, while the symbol `#`
creates an ordered one. The two can be mixed, e.g.

# Numbered item 1
** Bullet point 1
** Bullet point 2
** Bullet point 3
# Numbered item 2

Arguments:

* `start` - Can be a positive integer or "auto", defaults to "auto".
            Controls the starting number for the first item of the list.
"""


class ListItemNode(WrapperNode):
    """An entry in a list."""

    type = "list-item"

    def __init__(
        self,
        level: int,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
        content: Sequence[Node] | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info, content=content)

        self.level = level

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.level = self.level
        return new_node


class ListNode(Node, NodeContentMixin, NodeLabelsMixin):
    """A list."""

    type = "list"

    def __init__(
        self,
        ordered,
        main_node=False,
        start=1,
        content: Sequence[Node] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeContentMixin.__init__(self, content)
        NodeLabelsMixin.__init__(self, labels)

        self.ordered = ordered
        self.main_node = main_node
        self.start = start

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.ordered = self.ordered
        new_node.main_node = self.main_node
        new_node.start = self.start

        # Recursive deep copies.
        self._deepcopy_content(new_node)
        self._deepcopy_labels(new_node)

        return new_node
