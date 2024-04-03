from mau.nodes.page import Node


class ContentNode(Node):
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
        uris,
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
        self.content_type = content_type
        self.title = title
        self.uris = uris

    def _custom_dict(self):
        return {
            "content_type": self.content_type,
            "title": self.title,
            "uris": self.uris,
        }


class ContentImageNode(Node):
    """An image included in the page."""

    node_type = "content_image"

    def __init__(
        self,
        uri,
        alt_text=None,
        classes=None,
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
