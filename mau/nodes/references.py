from mau.nodes.nodes import Node


class ReferenceNode(Node):
    node_type = "reference"

    def __init__(
        self,
        content_type,
        number=None,
        title=None,
        reference_anchor=None,
        content_anchor=None,
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
        self.content_type = content_type
        self.number = number
        self.title = title
        self.reference_anchor = reference_anchor
        self.content_anchor = content_anchor

    def _custom_dict(self):
        return {
            "content_type": self.content_type,
            "number": self.number,
            "title": self.title,
            "reference_anchor": self.reference_anchor,
            "content_anchor": self.content_anchor,
        }

    def to_entry(self):
        return ReferencesEntryNode(
            content_type=self.content_type,
            number=self.number,
            title=self.title,
            reference_anchor=self.reference_anchor,
            content_anchor=self.content_anchor,
            parent=self.parent,
            parent_position=self.parent_position,
            children=self.children,
            subtype=self.subtype,
            args=self.args,
            kwargs=self.kwargs,
            tags=self.tags,
        )


class MacroReferenceNode(ReferenceNode):
    """Reference to stored content."""

    node_type = "reference"


class ReferencesEntryNode(ReferenceNode):
    """An entry of the list of references."""

    node_type = "references_entry"


class ReferencesNode(Node):
    """This instructs Mau to insert the content of references."""

    node_type = "references"

    def __init__(
        self,
        content_type,
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
        self.content_type = content_type

    def _custom_dict(self):
        return {
            "content_type": self.content_type,
        }
