from mau.nodes.nodes import Node


class FootnoteNode(Node):
    node_type = "footnote"

    def __init__(
        self,
        number=None,
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
        self.number = number
        self.reference_anchor = reference_anchor
        self.content_anchor = content_anchor

    def _custom_dict(self):
        return {
            "number": self.number,
            "reference_anchor": self.reference_anchor,
            "content_anchor": self.content_anchor,
        }

    def to_entry(self):
        return FootnotesEntryNode(
            number=self.number,
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


class MacroFootnoteNode(FootnoteNode):
    """A footnote created inside a piece of text."""

    node_type = "footnote"


class FootnotesEntryNode(FootnoteNode):
    """An entry of the list of footnotes."""

    node_type = "footnotes_entry"


class FootnotesNode(Node):
    """This instructs Mau to insert the list of footnotes."""

    node_type = "footnotes"
