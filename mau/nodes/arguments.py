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

    def __init__(
        self,
        key,
        value,
        parent=None,
        parent_position=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )
        self.key = key
        self.value = value

    def _custom_dict(self):
        return {
            "key": self.key,
            "value": self.value,
        }
