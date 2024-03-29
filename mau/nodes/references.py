from mau.nodes.nodes import SupaNode
from mau.nodes.page import PageNode


class ReferenceNode(SupaNode):
    node_type = "reference"

    def __init__(
        self,
        content_type,
        number=None,
        title=None,
        reference_anchor=None,
        content_anchor=None,
        parent=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
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
        }

    def to_entry(self):
        return ReferencesEntryNode(
            self.content_type,
            self.number,
            self.title,
            self.reference_anchor,
            self.content_anchor,
            self.parent,
            self.children,
            self.subtype,
            self.args,
            self.kwargs,
            self.tags,
        )


class MacroReferenceNode(ReferenceNode):
    """Reference to stored content."""

    node_type = "reference"


class ReferencesEntryNode(ReferenceNode):
    """An entry of the list of references."""

    node_type = "references_entry"


class ReferencesNode(SupaNode):
    """This instructs Mau to insert the content of references."""

    node_type = "references"

    def __init__(
        self,
        content_type,
        parent=None,
        children=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(
            parent=parent,
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
