from mau.nodes.nodes import Node, ValueNode, SupaNode, SupaValueNode


class WordNode(SupaValueNode):
    """This is a single word, it's used internally
    and eventually packed together with others into
    a TextNode
    """

    node_type = "word"


class TextNode(SupaValueNode):
    """This contains plain text and is created
    as a collation of multiple WordNode objects
    """

    node_type = "text"


class RawNode(SupaValueNode):
    """This contains plain text but the content
    should be treated as raw data and left untouched.
    E.g. it shouldn't be escaped.
    """

    node_type = "raw"


class VerbatimNode(SupaValueNode):
    """This node contains verbatim text."""

    node_type = "verbatim"


class SentenceNode(SupaNode):
    """A recursive container node.

    This node represents the content of a paragraph, but it is recursive,
    while ParagraphNode is not.
    """

    node_type = "sentence"


class StyleNode(Node):
    """Describes the style applied to a node."""

    node_type = "style"

    def __init__(self, value, content):
        super().__init__()
        self.value = value
        self.content = content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "value": self.value,
            "content": self.content,
        }
