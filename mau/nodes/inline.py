# Inline nodes can be found inside a paragraph

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


class VerbatimNode(ValueNode):
    """This node contains verbatim text."""

    node_type = "verbatim"


class SentenceNode(Node):
    """A recursive container node.

    This node represents the content of a paragraph, but it is recursive,
    while ParagraphNode is not.
    """

    node_type = "sentence"

    def __init__(self, content):
        super().__init__()
        self.content = content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "content": self.content,
        }


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


class MacroNode(Node):
    """This node contains a macro, with a name and arguments."""

    node_type = "macro"

    def __init__(self, name, args=None, kwargs=None):
        super().__init__()
        self.name = name
        self.args = args or []
        self.kwargs = kwargs or {}

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "name": self.name,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class ClassNode(Node):
    """Text with one or more classes."""

    node_type = "class"

    def __init__(self, classes, content):
        super().__init__()
        self.classes = classes
        self.content = content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "classes": self.classes,
            "content": self.content,
        }


class LinkNode(Node):
    """This node contains a link."""

    node_type = "link"

    def __init__(self, target, text=None):
        super().__init__()
        self.target = target
        self.text = text

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "target": self.target,
            "text": self.text,
        }


class ImageNode(Node):
    """This node contains an inline image."""

    node_type = "image"

    def __init__(self, uri, alt_text=None, width=None, height=None):
        super().__init__()
        self.uri = uri
        self.alt_text = alt_text
        self.width = width
        self.height = height

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "uri": self.uri,
            "alt_text": self.alt_text,
            "width": self.width,
            "height": self.height,
        }


class ListItemNode(Node):
    """An entry in a list."""

    node_type = "list_item"

    def __init__(self, level, content):
        super().__init__()
        self.level = level
        self.content = content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "level": self.level,
            "content": self.content,
        }
