from mau.nodes.nodes import Node


class TocEntryNode(Node):
    """An entry of the Table of Contents.

    This node contains an entry of the Table of Contents.
    """

    node_type = "toc_entry"

    def __init__(
        self,
        value=None,
        anchor=None,
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
        self.value = value
        self.anchor = anchor

    def _custom_dict(self):
        return {
            "value": self.value,
            "anchor": self.anchor,
        }


class TocNode(Node):
    """A Table of Contents command.

    This node contains the headers that go into the ToC.
    """

    node_type = "toc"
