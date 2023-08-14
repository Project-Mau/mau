from mau.nodes.nodes import Node
from mau.nodes.page import PageNode


class ReferenceNode(Node):
    """Reference to stored content."""

    node_type = "reference"

    def __init__(
        self,
        content_type,
        name,
        category=None,
        content=None,
        number=None,
        title=None,
        reference_anchor=None,
        content_anchor=None,
    ):
        super().__init__()
        self.content_type = content_type
        self.name = name
        self.category = category
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
            "name": self.name,
            "category": self.category,
            "content": self.content,
            "number": self.number,
            "title": self.title,
            "reference_anchor": self.reference_anchor,
            "content_anchor": self.content_anchor,
        }


class ReferencesEntryNode(ReferenceNode):
    """An entry of the list of references."""

    node_type = "references_entry"


class CommandReferencesNode(PageNode):
    """This instructs Mau to insert the content of references."""

    node_type = "command_references"

    def __init__(
        self,
        entries,
        content_type=None,
        category=None,
        name=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.content_type = content_type
        self.category = category
        self.name = name
        self.entries = entries

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "content_type": self.content_type,
            "category": self.category,
            "name": self.name,
            "entries": self.entries,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
