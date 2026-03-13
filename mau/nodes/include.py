from __future__ import annotations

from collections.abc import Mapping, Sequence

from mau.nodes.block import BlockNode
from mau.nodes.footnote import FootnoteNode
from mau.nodes.header import HeaderNode
from mau.nodes.node import (
    Node,
    NodeArguments,
    NodeContentMixin,
    NodeInfo,
    NodeLabelsMixin,
)
from mau.nodes.raw import RawLineNode

INCLUDE_HELP = """
Syntax:

([URI+, ARGS])?
(@CONTROL)?
(. LABEL)*
<< TYPE(:URI+, ARGS)?

The include operator `<<` includes content of type TYPE using the provided ARGS.
The ARGS must contain at least one unnamed URI.
"""

INCLUDE_IMAGE_HELP = """
Syntax:

([URI, ALT_TEXT, CLASSES, ARGS])?
(@CONTROL)?
(. LABEL)*
<< image(:URI, ALT_TEXT, CLASSES, ARGS)?

The include operator `<< image` includes an image using the provided URI.
"""

INCLUDE_MAU_HELP = """
Syntax:

([URI, ARGS])?
(@CONTROL)?
(. LABEL)*
<< mau(:URI, ARGS)?

The include operator `<< mau` includes an external Mau file using the provided URI.
The file will be read and the content parsed and added to the parse tree of the document.
"""

INCLUDE_RAW_HELP = """
Syntax:

([URI, ARGS])?
(@CONTROL)?
(. LABEL)*
<< raw(:URI, ARGS)?

The include operator `<< raw` includes an external raw file using the provided URI.
The file will be read and the content added to the parse tree of the document as raw lines.
"""


class IncludeNode(Node, NodeLabelsMixin):
    """Content included in the page.

    This represents generic content included in the page.
    """

    type = "include"

    def __init__(
        self,
        ctype: str,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeLabelsMixin.__init__(self, labels)

        self.ctype = ctype

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.ctype = self.ctype

        # Recursive deep copies.
        self._deepcopy_labels(new_node)

        return new_node

    @property
    def custom_template_fields(self) -> dict:
        return {
            "ctype": self.ctype,
        }


class IncludeImageNode(Node, NodeLabelsMixin):
    """An image included in the page."""

    type = "include-image"

    def __init__(
        self,
        uri: str,
        alt_text: str | None = None,
        classes: Sequence[str] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeLabelsMixin.__init__(self, labels)

        self.uri = uri
        self.alt_text = alt_text
        self.classes = classes or []

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.uri = self.uri
        new_node.alt_text = self.alt_text
        new_node.classes = list(self.classes)

        # Recursive deep copies.
        self._deepcopy_labels(new_node)

        return new_node


class IncludeMauNode(Node, NodeContentMixin, NodeLabelsMixin):
    """Mau content included in the page.

    This represents Mau content included
    in the page from an external file.
    """

    type = "include-mau"

    def __init__(
        self,
        uri: str,
        content: Sequence[Node] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeContentMixin.__init__(self, content)
        NodeLabelsMixin.__init__(self, labels)

        self.uri = uri

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.uri = self.uri

        # Recursive deep copies.
        self._deepcopy_content(new_node)
        self._deepcopy_labels(new_node)

        return new_node


class IncludeRawNode(Node, NodeContentMixin, NodeLabelsMixin):
    """Raw content included in the page.

    This represents raw content included
    in the page from an external file.
    """

    type = "include-raw"

    def __init__(
        self,
        uri: str,
        content: Sequence[RawLineNode] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeContentMixin.__init__(self, content)
        NodeLabelsMixin.__init__(self, labels)

        self.uri = uri

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.uri = self.uri

        # Recursive deep copies.
        self._deepcopy_content(new_node)
        self._deepcopy_labels(new_node)

        return new_node


class FootnotesItemNode(Node):
    type = "footnotes-item"

    def __init__(
        self,
        footnote: FootnoteNode,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        self.footnote = footnote

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.footnote = self.footnote

        return new_node


class FootnotesNode(Node, NodeLabelsMixin):
    """The list of footnotes."""

    type = "footnotes"

    def __init__(
        self,
        footnotes: Sequence[FootnotesItemNode] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeLabelsMixin.__init__(self, labels)

        self.footnotes = footnotes or []

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.footnotes = [
            child.deepcopy(parent=new_node) for child in self.footnotes
        ]

        # Recursive deep copies.
        self._deepcopy_labels(new_node)

        return new_node


class TocItemNode(Node):
    """A Table of Contents.

    This node contains the headers that go into the ToC.
    """

    type = "toc-item"

    def __init__(
        self,
        header: HeaderNode,
        entries: Sequence[TocItemNode] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        self.header = header
        self.entries = entries or []

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.header = self.header
        new_node.entries = [child.deepcopy(parent=new_node) for child in self.entries]

        return new_node


class TocNode(Node, NodeLabelsMixin):
    """The Table of Contents."""

    type = "toc"

    def __init__(
        self,
        plain_entries: Sequence[HeaderNode] | None = None,
        nested_entries: Sequence[TocItemNode] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeLabelsMixin.__init__(self, labels)

        self.plain_entries = plain_entries or []
        self.nested_entries = nested_entries or []

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.plain_entries = [
            child.deepcopy(parent=new_node) for child in self.plain_entries
        ]
        new_node.nested_entries = [
            child.deepcopy(parent=new_node) for child in self.nested_entries
        ]

        # Recursive deep copies.
        self._deepcopy_labels(new_node)

        return new_node


class BlockGroupItemNode(Node):
    type = "blockgroup-item"

    def __init__(
        self,
        group: str,
        position: str,
        block: BlockNode | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        self.position = position
        self.block = block

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.position = self.position
        new_node.block = self.block.deepcopy(parent=new_node)

        return new_node

    @property
    def custom_template_fields(self) -> dict:
        return {
            "position": self.position,
        }


class BlockGroupNode(Node, NodeLabelsMixin):
    type = "blockgroup"

    def __init__(
        self,
        name: str,
        items: Mapping[str, BlockGroupItemNode] | None = None,
        labels: Mapping[str, Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        NodeLabelsMixin.__init__(self, labels)

        self.name = name
        self.items = items or {}

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.name = self.name
        new_node.items = {
            key: item.deepcopy(parent=new_node) for key, item in self.items.items()
        }

        # Recursive deep copies.
        self._deepcopy_labels(new_node)

        return new_node

    @property
    def custom_template_fields(self) -> dict:
        return {
            "name": self.name,
        }
