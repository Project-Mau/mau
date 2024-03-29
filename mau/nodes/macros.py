from mau.nodes.nodes import Node, SupaNode


class MacroNode(SupaNode):
    """This node contains a macro, with a name and arguments."""

    node_type = "macro"

    def __init__(
        self,
        name,
        args=None,
        kwargs=None,
        tags=None,
        subtype=None,
        parent=None,
    ):
        super().__init__(
            parent=parent, subtype=subtype, args=args, kwargs=kwargs, tags=tags
        )
        self.name = name

    def _custom_dict(self):
        return {
            "name": self.name,
        }


class MacroClassNode(SupaNode):
    """Text with one or more classes."""

    node_type = "macro__class"

    def __init__(
        self,
        classes,
        content,
        args=None,
        kwargs=None,
        tags=None,
        subtype=None,
        parent=None,
    ):
        super().__init__(
            parent=parent, subtype=subtype, args=args, kwargs=kwargs, tags=tags
        )
        self.classes = classes
        self.content = content

    def _custom_dict(self):
        return {
            "classes": self.classes,
            "content": self.content,
        }


class MacroLinkNode(SupaNode):
    """This node contains a link."""

    node_type = "macro__link"

    def __init__(
        self,
        target,
        text=None,
        args=None,
        kwargs=None,
        tags=None,
        subtype=None,
        parent=None,
    ):
        super().__init__(
            parent=parent, subtype=subtype, args=args, kwargs=kwargs, tags=tags
        )
        self.target = target
        self.text = text

    def _custom_dict(self):
        return {
            "target": self.target,
            "text": self.text,
        }


class MacroImageNode(SupaNode):
    """This node contains an inline image."""

    node_type = "macro__image"

    def __init__(
        self,
        uri,
        alt_text=None,
        width=None,
        height=None,
        args=None,
        kwargs=None,
        tags=None,
        subtype=None,
        parent=None,
    ):
        super().__init__(
            parent=parent, subtype=subtype, args=args, kwargs=kwargs, tags=tags
        )
        self.uri = uri
        self.alt_text = alt_text
        self.width = width
        self.height = height

    def _custom_dict(self):
        return {
            "uri": self.uri,
            "alt_text": self.alt_text,
            "width": self.width,
            "height": self.height,
        }
