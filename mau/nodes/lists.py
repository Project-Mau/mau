from mau.nodes.nodes import Node


class ListItemNode(Node):
    """An entry in a list."""

    node_type = "list_item"

    def __init__(
        self,
        level,
        parent=None,
        parent_position=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
        context=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
            context=context,
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
        start=1,
        parent=None,
        parent_position=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
        context=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
            context=context,
        )
        self.ordered = ordered
        self.main_node = main_node
        self.start = start

    def _custom_dict(self):
        return {
            "ordered": self.ordered,
            "main_node": self.main_node,
            "start": self.start,
        }
