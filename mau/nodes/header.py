from mau.nodes.nodes import Node


class HeaderNode(Node):
    """A header."""

    node_type = "header"

    def __init__(
        self,
        value=None,
        level=None,
        anchor=None,
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
        self.value = value
        self.level = level
        self.anchor = anchor

    def _custom_dict(self):
        return {
            "value": self.value,
            "level": self.level,
            "anchor": self.anchor,
        }
