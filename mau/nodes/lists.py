from mau.nodes.nodes import Node, SupaNode
from mau.nodes.page import PageNode


class ListItemNode(Node):
    """An entry in a list."""

    node_type = "list_item"

    def __init__(self, level, content):
        super().__init__()
        self.level = level
        self.content = content

    def asdict(self):
        return self._content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "level": self.level,
            "content": self.content,
        }


class ListNode(SupaNode):
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
