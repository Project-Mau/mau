from mau.nodes.nodes import Node
from mau.nodes.page import PageNode


class ListItemNode(Node):
    """An entry in a list."""

    node_type = "list_item"

    def __init__(self, level, content):
        super().__init__()
        self.level = level
        self.content = content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "level": self.level,
            "content": self.content,
        }


class ListNode(PageNode):
    """A list."""

    node_type = "list"

    def __init__(
        self,
        ordered,
        items,
        main_node=False,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(subtype, args, kwargs, tags)
        self.ordered = ordered
        self.items = items
        self.main_node = main_node

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "ordered": self.ordered,
            "items": self.items,
            "main_node": self.main_node,
            "subtype": self.subtype,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
