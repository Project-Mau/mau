# There are two types of elements in Mau, inline and block ones
# (the nomenclature is borrowed from HTML).
# Block elements are always on a new line, so they correspond to
# main items in the document, while inline elements can only appear
# inside a paragraph.


def extract_tags_from_kwargs(kwargs):
    tags_list = kwargs.pop("tags", "").split(",")

    # Remove empty strings and return
    return list(filter(None, tags_list))


class Node:
    node_type = "node"

    def asdict(self):
        return {"type": self.node_type}  # pragma: no cover

    def __eq__(self, other):
        return self.asdict() == other.asdict()


# Inline elements


class ValueNode(Node):
    node_type = "value_node"

    def __init__(self, value):
        self.value = value

    def asdict(self):
        return {"type": self.node_type, "value": self.value}


class ContainerNode(Node):
    node_type = "container_node"

    def __init__(self, content):
        self.content = content

    def asdict(self):
        return {"type": self.node_type, "content": [i.asdict() for i in self.content]}


class WrapperNode(ValueNode):
    node_type = "wrapper_node"

    def __init__(self, value, content):
        super().__init__(value)
        self.content = content

    def asdict(self):
        return {
            "type": self.node_type,
            "value": self.value,
            "content": self.content.asdict(),
        }


class WordNode(ValueNode):
    """This is a single word, it's used internally
    and eventually packed together with others into
    a TextNode
    """

    node_type = "word"


class TextNode(ValueNode):
    """This contains plain text and is created
    as a collation of multiple WordNode objects

    Attributes:
        value: the text contained in the node
    """

    node_type = "text"


class SentenceNode(ContainerNode):
    """A recursive container node.

    This node represents the content of a paragraph, but it is recursive,
    while :obj:`ParagraphNode` is not. It can contain other :obj:`SentenceNode`
    objects, or other types of nodes like :obj:`TextNode`,
    :obj:`StyleNode` or :obj:`MacroNode`.

    Attributes:
        content (:obj:`list`): a list of nodes contained in this node
    """

    node_type = "sentence"


class StyleNode(WrapperNode):
    """Describes the style applied to a node.

    It contains a single node that is styled with the given value.
    Currently Mau supports 2 styles represented by `*` and `_`
    but this node is agnostic.

    Attributes:
        value (:obj:`str`): the name of the style
        content (:obj:`SentenceNode`): a single node
    """

    node_type = "style"


class VerbatimNode(ValueNode):
    """Verbatim text.

    This node contains verbatim text.

    Attributes:
        value: the text contained in the node
    """

    node_type = "verbatim"


class ClassNode(Node):
    """Text with one or more class.

    This node contains text that has been assigned
    one or more classes.

    Attributes:
        value: the text contained in the node
        classes (:obj:`list`): the classes assigned to the text
    """

    node_type = "class"

    def __init__(self, classes, content):
        self.classes = classes
        self.content = content

    def asdict(self):
        return {
            "type": self.node_type,
            "classes": self.classes,
            "content": self.content.asdict(),
        }


class MacroNode(Node):
    """Base node for macros.

    This node contains a macro, with a name and arguments.

    Attributes:
        value: the name of the macro
        arguments: the string of arguments
    """

    node_type = "macro"

    def __init__(self, name, args=None, kwargs=None):
        self.name = name
        self.args = args or []
        self.kwargs = kwargs or {}

        try:
            self.value = self.args[0]
        except IndexError:
            self.value = None

    def asdict(self):
        return {
            "type": self.node_type,
            "name": self.name,
            "value": self.value,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class LinkNode(Node):
    """Link macro.

    This node contains a link.

    Attributes:
        target: the target of the link
        text: the text of the link
    """

    node_type = "link"

    def __init__(self, target, text):
        self.target = target
        self.text = text

    def asdict(self):
        return {
            "type": self.node_type,
            "target": self.target,
            "text": self.text,
        }


class ImageNode(Node):
    """Inline image.

    This node contains an inline image.

    Attributes:
        uri: the URI of the image
        alt_text: alternative text if the image is not available
        width: width of the image
        height: height fo the image
    """

    node_type = "image"

    def __init__(self, uri, alt_text=None, width=None, height=None):
        self.uri = uri
        self.alt_text = alt_text
        self.width = width
        self.height = height

    def asdict(self):
        return {
            "type": self.node_type,
            "uri": self.uri,
            "alt_text": self.alt_text,
            "width": self.width,
            "height": self.height,
        }


class FootnoteNode(Node):
    """Footnote definition/reference.

    This node contains a footnote definition or reference.

    Attributes:
       number: number of this footnote
       refanchor: anchor ID of the reference
       defanchor: anchor ID of the definition
    """

    node_type = "footnote"

    def __init__(self, number, refanchor, defanchor, content):
        self.number = number
        self.refanchor = refanchor
        self.defanchor = defanchor
        self.content = content

    def asdict(self):
        return {
            "type": self.node_type,
            "refanchor": self.refanchor,
            "defanchor": self.defanchor,
            "number": self.number,
            "content": [i.asdict() for i in self.content],
        }


class FootnoteRefNode(FootnoteNode):
    node_type = "footnote_ref"


class FootnoteDefNode(FootnoteNode):
    node_type = "footnote_def"


# Block elements


class HorizontalRuleNode(Node):
    """A horizontal rule."""

    def asdict(self):
        return {"type": "horizontal_rule"}


class ContentNode(Node):
    """Content included in the page.

    This represents generic content included in the page.

    Arguments:
        uri: the URI of the image
        title: caption of the image
        args: unnamed arguments
        kwargs: named arguments
    """

    node_type = "content"

    def __init__(self, uri, title=None, args=None, kwargs=None):
        self.uri = uri
        self.title = title
        self.kwargs = kwargs or {}
        self.args = args or []

    def asdict(self):
        return {
            "type": self.node_type,
            "uri": self.uri,
            "title": self.title.asdict() if self.title else None,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class ContentImageNode(Node):
    """An image included in the page.

    This represents an image included in the page.

    Arguments:
        uri: the URI of the image
        alt_text: alternative text if the image is not available
        classes (:obj:`list`): list of classes added to the image
        title: caption of the image
        kwargs: named arguments
    """

    node_type = "content_image"

    def __init__(self, uri, alt_text, classes=None, title=None, kwargs=None):
        self.uri = uri
        self.alt_text = alt_text
        self.classes = classes
        self.title = title
        self.kwargs = kwargs or {}

    def asdict(self):
        return {
            "type": self.node_type,
            "alt_text": self.alt_text,
            "uri": self.uri,
            "title": self.title.asdict() if self.title else None,
            "classes": self.classes,
            "kwargs": self.kwargs,
        }


class ParagraphNode(Node):
    """A paragraph.

    This is a wrapper around a single :obj:`SentenceNode`. This node
    is not recursive.

    Arguments:
        content (:obj:`SentenceNode`): the text of the paragraph
        args: unnamed arguments
        kwargs: named arguments
    """

    node_type = "paragraph"

    def __init__(self, content, args=None, kwargs=None):
        self.args = args or []
        self.kwargs = kwargs or {}
        self.content = content

    def asdict(self):
        return {
            "type": self.node_type,
            "content": self.content.asdict(),
            "args": self.args,
            "kwargs": self.kwargs,
        }


class HeaderNode(Node):
    """A header.

    This node represents a header.

    Arguments:
        value: the text in the header
        level: the level of the header (1 is most important)
        anchor: the ID anchor of this node
        kwargs: named arguments
    """

    node_type = "header"

    def __init__(self, value, level, anchor, kwargs=None):
        self.value = value
        self.level = level
        self.anchor = anchor
        self.kwargs = kwargs or {}
        self.tags = extract_tags_from_kwargs(self.kwargs)

    def asdict(self):
        return {
            "type": self.node_type,
            "value": self.value,
            "level": self.level,
            "anchor": self.anchor,
            "tags": self.tags,
            "kwargs": self.kwargs,
        }


class BlockNode(Node):
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
    """

    node_type = "block"

    def __init__(
        self,
        blocktype,
        content,
        secondary_content,
        title=None,
        classes=None,
        engine=None,
        preprocessor=None,
        args=None,
        kwargs=None,
    ):
        self.blocktype = blocktype
        self.content = content
        self.secondary_content = secondary_content
        self.title = title
        self.classes = classes or []
        self.engine = engine
        self.preprocessor = preprocessor
        self.args = args or []
        self.kwargs = kwargs or {}

    def asdict(self):
        return {
            "type": self.node_type,
            "blocktype": self.blocktype,
            "content": [i.asdict() for i in self.content],
            "secondary_content": [i.asdict() for i in self.secondary_content],
            "classes": self.classes,
            "engine": self.engine,
            "preprocessor": self.preprocessor,
            "args": self.args,
            "kwargs": self.kwargs,
            "title": self.title.asdict() if self.title else None,
        }


class SourceNode(Node):
    """A block of verbatim text or source code.

    This node contains verbatim text or source code.

    Arguments:
        language: the language of the code contained in this block
        callouts: callouts for this source code
                  {"markers": [(linenum, name)], "contents": {name:text}}
        highlights: list of lines that have to be highlighted
        delimiter: callouts delimiter
        code: content of the block
        title: title of this block
        kwargs: named arguments
    """

    node_type = "source"

    def __init__(
        self, language, callouts, highlights, delimiter, code, title=None, kwargs=None
    ):
        self.language = language
        self.callouts = callouts
        self.highlights = highlights
        self.delimiter = delimiter
        self.code = code
        self.title = title
        self.kwargs = kwargs or {}

    def asdict(self):
        return {
            "type": self.node_type,
            "language": self.language,
            "callouts": self.callouts,
            "highlights": self.highlights,
            "delimiter": self.delimiter,
            "code": [i.asdict() for i in self.code],
            "title": self.title.asdict() if self.title else None,
            "kwargs": self.kwargs,
        }


class CommandNode(Node):
    """A Mau command.

    This represents a command issued in a Mau document.

    Arguments:
        name: the name of the command
        args: unnamed arguments
        kwargs: named arguments
    """

    node_type = "command"

    def __init__(self, name, args=None, kwargs=None):
        self.args = args or []
        self.kwargs = kwargs or {}
        self.name = name

    def asdict(self):
        return {
            "type": self.node_type,
            "name": self.name,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class FootnotesNode(Node):
    """A list of footnote definitions.

    This node contains the footnote definitions.

    Arguments:
        entries: a list of FootnoteDefNode objects
    """

    node_type = "footnotes"

    def __init__(self, entries=None):
        self.entries = entries or []

    def asdict(self):
        return {"type": self.node_type, "entries": [i.asdict() for i in self.entries]}


class TocNode(Node):
    """A Table of Contents.

    This node contains the entries of the Table of Contents.

    Arguments:
        entries: a list of TocEntryNode objects
    """

    node_type = "toc"

    def __init__(self, entries=None):
        self.entries = entries or []

    def asdict(self):
        return {"type": self.node_type, "entries": [i.asdict() for i in self.entries]}


class TocEntryNode(Node):
    """An entry of the Table of Contents.

    This node contains an entry of the Table of Contents.

    Arguments:
        level: level of this entry (level of the header)
        text: the text of the entry
        anchor: the ID of the header
        children: child entries
    """

    node_type = "toc_entry"

    def __init__(self, header_node, children=None):
        self.header = header_node
        self.children = children or []

    def asdict(self):
        return {
            "type": self.node_type,
            "header": self.header.asdict(),
            "children": [i.asdict() for i in self.children],
        }


class ListNode(Node):
    """A list.

    This node contains an ordered or unordered list.

    Arguments:
        ordered (:obj:`bool`): whether the list is ordered or not
        items (:obj:`list`): entries contained in this entry
        main_node (:obj:`bool`): whether this is the main node of the list
    """

    node_type = "list"

    def __init__(self, ordered, items, main_node=False):
        self.ordered = ordered
        self.items = items
        self.main_node = main_node

    def asdict(self):
        return {
            "type": self.node_type,
            "ordered": self.ordered,
            "items": [i.asdict() for i in self.items],
            "main_node": self.main_node,
        }


class ListItemNode(Node):
    """An entry in a list.

    This node contains an entry of an ordered or unordered list.

    Arguments:
        level: the level of depth of this entry in the list
        content: the content of the entry
    """

    node_type = "list_item"

    def __init__(self, level, content):
        self.level = level
        self.content = content

    def asdict(self):
        return {
            "type": self.node_type,
            "level": self.level,
            "content": self.content.asdict(),
        }


class DocumentNode(ContainerNode):
    """A document.

    This node represents the full document.

    Arguments:
        content: the content of the document
    """

    node_type = "document"
