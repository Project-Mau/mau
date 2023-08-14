from mau.nodes.nodes import Node
from mau.nodes.page import PageNode


class FootnoteNode(Node):
    """A footnote created inside a piece of text."""

    node_type = "footnote"

    def __init__(
        self, content=None, number=None, reference_anchor=None, content_anchor=None
    ):
        super().__init__()
        self.content = content
        self.number = number
        self.reference_anchor = reference_anchor
        self.content_anchor = content_anchor

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "content": self.content,
            "number": self.number,
            "reference_anchor": self.reference_anchor,
            "content_anchor": self.content_anchor,
        }


class FootnotesEntryNode(FootnoteNode):
    """An entry of the list of footnotes."""

    node_type = "footnotes_entry"


class CommandFootnotesNode(PageNode):
    """This instructs Mau to insert the list of footnotes."""

    node_type = "command_footnotes"

    def __init__(self, entries, args=None, kwargs=None, tags=None):
        super().__init__(args, kwargs, tags)
        self.entries = entries

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "entries": self.entries,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
