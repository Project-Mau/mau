from mau.nodes.nodes import Node


class CalloutsEntryNode(Node):
    # This is an entry in the list of callouts after source code

    node_type = "callouts_entry"

    def __init__(
        self,
        marker,
        value,
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
        self.marker = marker
        self.value = value

    def _custom_dict(self):
        return {
            "value": self.value,
            "marker": self.marker,
        }


class CalloutNode(Node):
    # This is a marker near a source code line

    node_type = "callout"

    def __init__(
        self,
        line,
        marker,
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
        self.line = line
        self.marker = marker

    def _custom_dict(self):
        return {
            "line": self.line,
            "marker": self.marker,
        }


class SourceNode(Node):
    """A block of verbatim text or source code.

    This node contains verbatim text or source code.

    Arguments:
        language: the language of the code contained in this block
        callouts: a list of callout CalloutEntryNode objects
        markers: list of CalloutNode objects
        highlights: list of lines that have to be highlighted
        delimiter: callouts delimiter
        code: content of the block
        title: title of this block
        kwargs: named arguments
    """

    node_type = "source"

    def __init__(
        self,
        code=None,
        language="text",
        callouts=None,
        delimiter=":",
        markers=None,
        highlights=None,
        classes=None,
        title=None,
        preprocessor=None,
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
        self.code = code or []
        self.language = language
        self.callouts = callouts or []
        self.delimiter = delimiter
        self.markers = markers or []
        self.highlights = highlights or []
        self.classes = classes or []
        self.title = title
        self.preprocessor = preprocessor

    def _custom_dict(self):
        return {
            "code": self.code,
            "language": self.language,
            "callouts": self.callouts,
            "delimiter": self.delimiter,
            "markers": self.markers,
            "highlights": self.highlights,
            "classes": self.classes,
            "title": self.title,
            "preprocessor": self.preprocessor,
        }
