from mau.nodes.page import PageNode


class BlockNode(PageNode):
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
        content,
        secondary_content,
        subtype=None,
        classes=None,
        title=None,
        engine=None,
        preprocessor=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(subtype, args, kwargs, tags)
        self.content = content
        self.secondary_content = secondary_content
        self.title = title
        self.classes = classes or []
        self.engine = engine
        self.preprocessor = preprocessor

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "subtype": self.subtype,
            "content": self.content,
            "secondary_content": self.secondary_content,
            "title": self.title,
            "classes": self.classes,
            "engine": self.engine,
            "preprocessor": self.preprocessor,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
