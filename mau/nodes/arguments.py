from mau.nodes.nodes import Node, ValueNode


class UnnamedArgumentNode(ValueNode):
    """
    This node contains an unnamed argument.
    """

    node_type = "unnamed_argument"


class NamedArgumentNode(Node):
    """
    This node contains a named argument.
    """

    node_type = "named_argument"

    def __init__(self, key, value):
        super().__init__()
        self.key = key
        self.value = value

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "key": self.key,
            "value": self.value,
        }
