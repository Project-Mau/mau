# Page nodes can be found at top level in a page

from mau.nodes.nodes import Node


class PageNode(Node):
    node_type = "page_node"

    def __init__(
        self,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__()
        self.args = args or []
        self.kwargs = kwargs or {}
        self.tags = tags or []

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


class HorizontalRuleNode(PageNode):
    """A horizontal rule."""

    node_type = "horizontal_rule"


class ContainerNode(PageNode):
    node_type = "container"

    def __init__(
        self,
        content,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.content = content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "content": self.content,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


class DocumentNode(ContainerNode):
    """A document.

    This node represents the full document.

    Arguments:
        content: the content of the document
    """

    node_type = "document"
