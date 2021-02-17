from dataclasses import dataclass


class Node:
    node_type = "node"

    def asdict(self):
        return {"type": self.node_type}  # pragma: no cover


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
    # INLINE
    # This is a single word, it's used internally
    # and eventually packed together with others into
    # a TextNode
    node_type = "word"


class TextNode(ValueNode):
    # INLINE
    # This contains plain text and is created
    # as a collation of multiple WordNode objects
    node_type = "text"


class SentenceNode(ContainerNode):
    # INLINE
    # This is a container of TextNode objects and
    # other inline nodes like StyleNodes or MacroNodes
    # This is potentially recursive as inline nodes can
    # contain SentenceNodes.
    node_type = "sentence"


class StyleNode(WrapperNode):
    # INLINE
    # This cointains a single node that is styled with the given value
    node_type = "style"


class VerbatimNode(ValueNode):
    # INLINE
    node_type = "verbatim"


class ClassNode(ValueNode):
    # INLINE
    content: Node
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
    node_type = "macro"

    def __init__(self, value, args=None, kwargs=None):
        self.value = value
        self.args = args or []
        self.kwargs = kwargs or {}

    def asdict(self):
        return {
            "type": self.node_type,
            "value": self.value,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class LinkNode(Node):
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
    node_type = "footnote"

    def __init__(self, number, refanchor, defanchor):
        self.number = number
        self.refanchor = refanchor
        self.defanchor = defanchor

    def asdict(self):
        return {
            "type": self.node_type,
            "refanchor": self.refanchor,
            "defanchor": self.defanchor,
            "number": self.number,
        }


#############################################################################


class PageNode(Node):
    node_type = "page_node"

    def __init__(self, args=None, kwargs=None):
        self.args = args or []
        self.kwargs = kwargs or {}

    def asdict(self):
        return {"type": self.node_type}  # pragma: no cover


class PageValueNode(PageNode):
    node_type = "page_value_node"

    def __init__(self, value, args=None, kwargs=None):
        super().__init__(args, kwargs)
        self.value = value

    def asdict(self):
        return {
            "type": self.node_type,
            "value": self.value,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class HorizontalRuleNode(PageNode):
    def asdict(self):
        return {"type": "horizontal_rule"}


class ContentImageNode(PageNode):
    node_type = "content_image"

    def __init__(self, uri, alt_text, title=None, args=None, kwargs=None):
        super().__init__(args, kwargs)
        self.uri = uri
        self.alt_text = alt_text
        self.title = title

    def asdict(self):
        return {
            "type": self.node_type,
            "alt_text": self.alt_text,
            "uri": self.uri,
            "title": self.title.asdict() if self.title else None,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class ParagraphNode(PageNode):
    # DOCUMENT
    # This is a wrapper around a single SentenceNode, but is
    # not recursive.
    node_type = "paragraph"

    def __init__(self, content, args=None, kwargs=None):
        super().__init__(args, kwargs)
        self.content = content

    def asdict(self):
        return {
            "type": self.node_type,
            "content": self.content.asdict(),
            "args": self.args,
            "kwargs": self.kwargs,
        }


@dataclass
class HeaderNode(PageValueNode):
    # DOCUMENT
    node_type = "header"

    def __init__(self, value, level, anchor, args=None, kwargs=None):
        super().__init__(value, args, kwargs)
        self.level = level
        self.anchor = anchor

    def asdict(self):
        d = super().asdict()
        d.update(
            {
                "level": self.level,
                "anchor": self.anchor,
            }
        )
        return d


class BlockNode(PageNode):
    # DOCUMENT
    def __init__(self, content, secondary_content, args=None, kwargs=None, title=None):
        super().__init__(args, kwargs)
        self.content = content
        self.secondary_content = secondary_content
        self.title = title

    def asdict(self):
        return {
            "type": "block",
            "content": [i.asdict() for i in self.content],
            "secondary_content": [i.asdict() for i in self.secondary_content],
            "args": self.args,
            "kwargs": self.kwargs,
            "title": self.title.asdict() if self.title else None,
        }


class SourceNode(PageNode):
    # DOCUMENT
    def __init__(self, language, callouts, code, args=None, kwargs=None, title=None):
        super().__init__(args, kwargs)
        self.language = language
        self.callouts = callouts
        self.code = code
        self.title = title

    def asdict(self):
        return {
            "type": "source",
            "language": self.language,
            "callouts": self.callouts,
            "code": [i.asdict() for i in self.code],
            "title": self.title.asdict() if self.title else None,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class RawNode(PageNode):
    # DOCUMENT
    def __init__(self, content, args=None, kwargs=None):
        super().__init__(args, kwargs)
        self.content = content

    def asdict(self):
        return {
            "type": "raw",
            "content": [i.asdict() for i in self.content],
            "args": self.args,
            "kwargs": self.kwargs,
        }


class AdmonitionNode(PageNode):
    # DOCUMENT
    def __init__(
        self, admclass, icon, label, content, args=None, kwargs=None, title=None
    ):
        super().__init__(args, kwargs)
        self.admclass = admclass
        self.icon = icon
        self.label = label
        self.content = content

    def asdict(self):
        return {
            "type": "admonition",
            "class": self.admclass,
            "icon": self.icon,
            "label": self.label,
            "content": [i.asdict() for i in self.content],
            "args": self.args,
            "kwargs": self.kwargs,
        }


class CommandNode(PageNode):
    # DOCUMENT
    def __init__(self, name, args=None, kwargs=None):
        super().__init__(args, kwargs)
        self.name = name

    def asdict(self):
        return {
            "type": "command",
            "name": self.name,
            "args": self.args,
            "kwargs": self.kwargs,
        }


class QuoteNode(PageNode):
    # DOCUMENT
    def __init__(self, attribution, content, args=None, kwargs=None):
        super().__init__(args, kwargs)
        self.attribution = attribution
        self.content = content

    def asdict(self):
        return {
            "type": "quote",
            "attribution": self.attribution,
            "content": [i.asdict() for i in self.content],
            "args": self.args,
            "kwargs": self.kwargs,
        }


class FootnoteContentNode(PageNode):
    node_type = "footnote_content"

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


class TocNode:
    def __init__(self, level, value, anchor):
        self.value = value
        self.anchor = anchor
        self.children = []

    def asdict(self):
        return {
            "value": self.value,
            "anchor": self.anchor,
            "children": [i.asdict() for i in self.children],
        }


class ListNode(PageNode):
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


class ListItemNode(PageNode):
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


class DocumentNode(Node):
    def __init__(self, content):
        self.content = content

    def asdict(self):
        return {
            "type": "document",
            "content": [i.asdict() for i in self.content],
        }
