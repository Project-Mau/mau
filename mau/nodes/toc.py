from mau.nodes.nodes import Node
from mau.nodes.page import PageNode


class TocEntryNode(Node):
    """An entry of the Table of Contents.

    This node contains an entry of the Table of Contents.
    """

    node_type = "toc_entry"

    def __init__(
        self,
        value,
        anchor,
        children=None,
        tags=None,
    ):
        super().__init__()
        self.value = value
        self.anchor = anchor
        self.children = children or []
        self.tags = tags or []

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "value": self.value,
            "anchor": self.anchor,
            "children": self.children,
            "tags": self.tags,
        }


class TocNode(PageNode):
    """A Table of Contents command.

    This node contains the headers that go into the ToC.
    """

    node_type = "toc"

    def __init__(
        self,
        entries,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(subtype, args, kwargs, tags)
        self.entries = entries

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "entries": self.entries,
            "subtype": self.subtype,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
