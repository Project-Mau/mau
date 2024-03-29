from mau.nodes.nodes import SupaNode


class BlockNode(SupaNode):
    """A block.

    This node contains a generic block.

    Arguments:
        blocktype: the type of this block
        content: content of the block
        secondary_content: secondary content of this block
        title: title of this block
        classes: a comma-separated list of classes
        engine: the engine used to render this block
        preprocessor: the preprocessor used for this block
        args: unnamed arguments
        kwargs: named arguments
        tags: tags
    """

    node_type = "block"

    def __init__(
        self,
        classes=None,
        title=None,
        engine=None,
        preprocessor=None,
        parent=None,
        children=None,
        secondary_children=None,
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
        self.classes = classes or []
        self.title = title
        self.engine = engine
        self.preprocessor = preprocessor
        self.secondary_children = secondary_children or []

    def _custom_dict(self):
        return {
            "classes": self.classes,
            "title": self.title,
            "engine": self.engine,
            "preprocessor": self.preprocessor,
            "secondary_children": self.secondary_children,
        }
