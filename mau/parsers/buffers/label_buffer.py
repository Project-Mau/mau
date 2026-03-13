from __future__ import annotations

from mau.nodes.label import LabelNode


class LabelBuffer:
    """A buffer that stores a dictionary
    of labels that will be added to another
    node as children."""

    def __init__(self):
        # This is where the buffer keeps the
        # stored children.
        self.labels: dict[str, LabelNode] = {}

    def push(
        self,
        role: str,
        node: LabelNode,
    ):
        # Store the given label node.
        self.labels[role] = node

    def pop(self) -> dict[str, LabelNode]:
        # Retrieve the stored labels
        # and reset the internal slot.
        labels = self.labels

        self.labels = {}

        return labels
