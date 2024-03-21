from mau.nodes.nodes import Node


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


class MacroClassNode(Node):
    """Text with one or more classes."""

    node_type = "macro__class"

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


class MacroLinkNode(Node):
    """This node contains a link."""

    node_type = "macro__link"

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


class MacroImageNode(Node):
    """This node contains an inline image."""

    node_type = "macro__image"

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
