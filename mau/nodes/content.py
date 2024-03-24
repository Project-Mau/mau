from mau.nodes.page import PageNode


class ContentNode(PageNode):
    """Content included in the page.

    This represents generic content included in the page.

    Arguments:
        content_type: the type of content
        title: caption of the image
        args: unnamed arguments
        kwargs: named arguments
        tags: tags
    """

    node_type = "content"

    def __init__(
        self,
        content_type,
        title=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.content_type = content_type
        self.title = title

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "content_type": self.content_type,
            "title": self.title,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


class ContentImageNode(PageNode):
    """An image included in the page."""

    node_type = "content_image"

    def __init__(
        self,
        uri,
        alt_text=None,
        classes=None,
        title=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.uri = uri
        self.classes = classes
        self.title = title
        self.alt_text = alt_text

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "uri": self.uri,
            "alt_text": self.alt_text,
            "classes": self.classes,
            "title": self.title,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }