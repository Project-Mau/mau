# Page nodes can be found at top level in a page

from mau.nodes.nodes import Node, SupaNode


class PageNode(Node):
    node_type = "page_node"

    def __init__(
        self,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__()
        self.subtype = subtype
        self.args = args or []
        self.kwargs = kwargs or {}
        self.tags = tags or []

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "subtype": self.subtype,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


class HorizontalRuleNode(SupaNode):
    """A horizontal rule."""

    node_type = "horizontal_rule"


class ContainerNode(SupaNode):
    node_type = "container"


class DocumentNode(ContainerNode):
    """A document.

    This node represents the full document.

    Arguments:
        content: the content of the document
    """

    node_type = "document"
