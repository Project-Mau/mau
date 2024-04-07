from mau.nodes.nodes import Node


class MacroNode(Node):
    """This node contains a macro, with a name and arguments."""

    node_type = "macro"

    def __init__(
        self,
        name,
        parent=None,
        parent_position=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )
        self.name = name

    def _custom_dict(self):
        return {
            "name": self.name,
        }


class MacroClassNode(Node):
    """Text with one or more classes."""

    node_type = "macro.class"

    def __init__(
        self,
        classes,
        parent=None,
        parent_position=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )
        self.classes = classes

    def _custom_dict(self):
        return {
            "classes": self.classes,
        }


class MacroLinkNode(Node):
    """This node contains a link."""

    node_type = "macro.link"

    def __init__(
        self,
        target,
        parent_position=None,
        parent=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )
        self.target = target

    def _custom_dict(self):
        return {
            "target": self.target,
        }


class MacroImageNode(Node):
    """This node contains an inline image."""

    node_type = "macro.image"

    def __init__(
        self,
        uri,
        alt_text=None,
        width=None,
        height=None,
        parent_position=None,
        parent=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
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


class MacroHeaderNode(Node):
    """This node contains a link to a header node."""

    node_type = "macro.header"

    def __init__(
        self,
        header_id,
        header=None,
        parent_position=None,
        parent=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
            parent_position=parent_position,
            children=children,
            subtype=subtype,
            args=args,
            kwargs=kwargs,
            tags=tags,
        )
        self.header_id = header_id
        self.header = header

    def _custom_dict(self):
        return {
            "header_id": self.header_id,
            "header": self.header,
        }
