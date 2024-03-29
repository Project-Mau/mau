from mau.nodes.page import SupaNode


class ContentNode(SupaNode):
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
        uri_args=None,
        uri_kwargs=None,
        title=None,
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
        self.title = title
        self.uri_args = uri_args
        self.uri_kwargs = uri_kwargs

    def _custom_dict(self):
        return {
            "content_type": self.content_type,
            "title": self.title,
            "uri_args": self.uri_args,
            "uri_kwargs": self.uri_kwargs,
        }


class ContentImageNode(SupaNode):
    """An image included in the page."""

    node_type = "content_image"

    def __init__(
        self,
        uri,
        alt_text=None,
        classes=None,
        title=None,
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
        self.uri = uri
        self.title = title
        self.alt_text = alt_text
        self.classes = classes

    def _custom_dict(self):
        return {
            "uri": self.uri,
            "title": self.title,
            "alt_text": self.alt_text,
            "classes": self.classes,
        }
