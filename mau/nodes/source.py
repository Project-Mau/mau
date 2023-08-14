from mau.nodes.nodes import Node
from mau.nodes.page import PageNode


class CalloutsEntryNode(Node):
    # This is an entry in the list of callouts after source code

    node_type = "callouts_entry"

    def __init__(self, marker, value):
        super().__init__()
        self.marker = marker
        self.value = value

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "marker": self.marker,
            "value": self.value,
        }


class CalloutNode(Node):
    # This is a marker near a source code line

    node_type = "callout"

    def __init__(self, line, marker):
        super().__init__()
        self.line = line
        self.marker = marker

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "line": self.line,
            "marker": self.marker,
        }


class SourceNode(PageNode):
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
        blocktype="default",
        code=None,
        language="text",
        callouts=None,
        delimiter=":",
        markers=None,
        highlights=None,
        classes=None,
        title=None,
        preprocessor=None,
        args=None,
        kwargs=None,
        tags=None,
    ):
        super().__init__(args, kwargs, tags)
        self.blocktype = blocktype
        self.code = code or []
        self.language = language
        self.callouts = callouts or []
        self.markers = markers or []
        self.delimiter = delimiter
        self.highlights = highlights or []
        self.classes = classes or []
        self.title = title
        self.preprocessor = preprocessor

    @property
    def _content(self):
        return {
            "type": self.node_type,
            "blocktype": self.blocktype,
            "code": self.code,
            "language": self.language,
            "callouts": self.callouts,
            "markers": self.markers,
            "delimiter": self.delimiter,
            "highlights": self.highlights,
            "classes": self.classes,
            "title": self.title,
            "preprocessor": self.preprocessor,
            "args": self.args,
            "kwargs": self.kwargs,
            "tags": self.tags,
        }
