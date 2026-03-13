from __future__ import annotations

from mau.nodes.node_arguments import NodeArguments


class ArgumentsBuffer:
    """This is a buffer for arguments
    collected in the source text."""

    def __init__(self):
        # This is where the buffer keeps the
        # stored arguments.
        self.arguments: NodeArguments | None = None

    def push(self, arguments: NodeArguments):
        # Store the given arguments.
        self.arguments = arguments

    def pop(self) -> NodeArguments | None:
        # Retrieve the stored arguments
        # and reset the internal slot.
        arguments = self.arguments
        self.arguments = None

        return arguments

    def pop_or_default(self) -> NodeArguments:
        # Retrieve the stored arguments
        # and reset the internal slot.
        # Return an empty NodeArguments object
        # if nothing is stored.
        return self.pop() or NodeArguments()
