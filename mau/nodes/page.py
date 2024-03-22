# Page nodes can be found at top level in a page

from mau.nodes.nodes import Node


class PageNode(Node):
    node_type = "page_node"

    def __init__(
        self,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__()
        self.args = args or []
        self.kwargs = kwargs or {}
        self.tags = tags or []

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


class HorizontalRuleNode(PageNode):
    """A horizontal rule."""

    node_type = "horizontal_rule"


class ParagraphNode(PageNode):
    """A paragraph."""

    node_type = "paragraph"

    def __init__(
        self,
        content,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.content = content
        self.subtype = subtype

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "subtype": self.subtype,
            "content": self.content,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


class HeaderNode(PageNode):
    """A header."""

    node_type = "header"

    def __init__(
        self,
        value,
        level,
        anchor,
        subtype=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.subtype = subtype
        self.value = value
        self.level = level
        self.anchor = anchor

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "subtype": self.subtype,
            "value": self.value,
            "level": self.level,
            "anchor": self.anchor,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


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
        super().__init__(args, kwargs, tags)
        self.subtype = subtype
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


class ContainerNode(PageNode):
    node_type = "container"

    def __init__(
        self,
        content,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.content = content

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "content": self.content,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }


class DocumentNode(ContainerNode):
    """A document.

    This node represents the full document.

    Arguments:
        content: the content of the document
    """

    node_type = "document"
