from mau.nodes.page import PageNode


class ParagraphNode(PageNode):
    """A paragraph."""

    node_type = "paragraph"

    def __init__(
        self,
        content,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(subtype, args, kwargs, tags)
        self.content = content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "subtype": self.subtype,
            "content": self.content,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
