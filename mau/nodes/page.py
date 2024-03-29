# Page nodes can be found at top level in a page

from mau.nodes.nodes import SupaNode


class HorizontalRuleNode(SupaNode):
    """A horizontal rule."""

    node_type = "horizontal_rule"


class ContainerNode(SupaNode):
    node_type = "container"


class DocumentNode(SupaNode):
    """A document.

    This node represents the full document.

    Arguments:
        content: the content of the document
    """

    node_type = "document"
