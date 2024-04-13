# Page nodes can be found at top level in a page

from mau.nodes.nodes import Node


class HorizontalRuleNode(Node):
    """A horizontal rule."""

    node_type = "horizontal_rule"


class ContainerNode(Node):
    node_type = "container"

    def clone(self):
        return self.__class__(
            parent=self.parent,
            parent_position=self.parent_position,
            children=self.children,
            subtype=self.subtype,
            args=self.args,
            kwargs=self.kwargs,
            tags=self.tags,
        )


class DocumentNode(ContainerNode):
    """A document.

    This node represents the full document.

    Arguments:
        content: the content of the document
    """

    node_type = "document"
