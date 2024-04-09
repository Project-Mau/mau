from mau.nodes.nodes import Node


class ParagraphNode(Node):
    """A paragraph."""

    node_type = "paragraph"

    def __init__(
        self,
        title=None,
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
        self.title = title

    def _custom_dict(self):
        return {
            "title": self.title,
        }
