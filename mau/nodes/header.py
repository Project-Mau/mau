from mau.nodes.page import PageNode


class HeaderNode(PageNode):
    """A header."""

    node_type = "header"

    def __init__(
        self,
        value,
        level,
        anchor,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.subtype = subtype
        self.value = value
        self.level = level
        self.anchor = anchor

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "subtype": self.subtype,
            "value": self.value,
            "level": self.level,
            "anchor": self.anchor,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
