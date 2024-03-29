from mau.nodes.nodes import Node


class ListItemNode(Node):
    """An entry in a list."""

    node_type = "list_item"

    def __init__(
        self,
        level,
        main_node=False,
        parent=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )
        self.level = level

    def _custom_dict(self):
        return {
            "level": self.level,
        }


class ListNode(Node):
    """A list."""

    node_type = "list"

    def __init__(
        self,
        ordered,
        main_node=False,
        parent=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )
        self.ordered = ordered

        self.main_node = main_node

    def _custom_dict(self):
        return {
            "ordered": self.ordered,
            "main_node": self.main_node,
        }
