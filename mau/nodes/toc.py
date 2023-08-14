from mau.nodes.page import PageNode


class TocNode(PageNode):
    """A Table of Contents.

    This node contains the entries of the Table of Contents.
    """

    node_type = "toc"

    def __init__(self, entries, args=None, kwargs=None, tags=None):
        super().__init__(args, kwargs, tags)
        self.entries = entries

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "entries": self.entries,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


class TocEntryNode(PageNode):
    """An entry of the Table of Contents.

    This node contains an entry of the Table of Contents.
    """

    node_type = "toc_entry"

    def __init__(self, value, anchor, children=None, args=None, kwargs=None, tags=None):
        super().__init__(args, kwargs, tags)
        self.value = value
        self.anchor = anchor
        self.children = children or []

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "value": self.value,
            "anchor": self.anchor,
            "children": self.children,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
