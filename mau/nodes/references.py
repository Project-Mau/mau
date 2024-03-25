from mau.nodes.nodes import Node
from mau.nodes.page import PageNode


class ReferenceNode(Node):
    node_type = "reference"

    def __init__(
        self,
        content_type,
        content=None,
        number=None,
        title=None,
        reference_anchor=None,
        content_anchor=None,
    ):
        super().__init__()
        self.content_type = content_type
        self.content = content or []
        self.number = number
        self.title = title
        self.reference_anchor = reference_anchor
        self.content_anchor = content_anchor

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "content_type": self.content_type,
            "content": self.content,
            "number": self.number,
            "title": self.title,
            "reference_anchor": self.reference_anchor,
            "content_anchor": self.content_anchor,
        }

    def to_entry(self):
        return ReferencesEntryNode(
            self.content_type,
            self.content,
            self.number,
            self.title,
            self.reference_anchor,
            self.content_anchor,
        )


class MacroReferenceNode(ReferenceNode):
    """Reference to stored content."""

    node_type = "reference"


class ReferencesEntryNode(ReferenceNode):
    """An entry of the list of references."""

    node_type = "references_entry"


class ReferencesNode(PageNode):
    """This instructs Mau to insert the content of references."""

    node_type = "references"

    def __init__(
        self,
        entries,
        content_type=None,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.content_type = content_type
        self.entries = entries
        self.subtype = subtype

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "content_type": self.content_type,
            "entries": self.entries,
            "subtype": self.subtype,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
