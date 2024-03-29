# Page nodes can be found at top level in a page

from mau.nodes.nodes import Node


class HorizontalRuleNode(Node):
    """A horizontal rule."""

    node_type = "horizontal_rule"


class ContainerNode(Node):
    node_type = "container"


class DocumentNode(Node):
    """A document.

    This node represents the full document.

    Arguments:
        content: the content of the document
    """

    node_type = "document"
