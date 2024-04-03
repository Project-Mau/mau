from mau.nodes.nodes import Node, ValueNode


class WordNode(ValueNode):
    """This is a single word, it's used internally
    and eventually packed together with others into
    a TextNode
    """

    node_type = "word"


class TextNode(ValueNode):
    """This contains plain text and is created
    as a collation of multiple WordNode objects
    """

    node_type = "text"


class RawNode(ValueNode):
    """This contains plain text but the content
    should be treated as raw data and left untouched.
    E.g. it shouldn't be escaped.
    """

    node_type = "raw"


class VerbatimNode(ValueNode):
    """This node contains verbatim text."""

    node_type = "verbatim"


class SentenceNode(Node):
    """A recursive container node.

    This node represents the content of a paragraph, but it is recursive,
    while ParagraphNode is not.
    """

    node_type = "sentence"


class StyleNode(ValueNode):
    """Describes the style applied to a node."""

    node_type = "style"
