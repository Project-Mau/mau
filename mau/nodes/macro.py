from collections.abc import Sequence

from mau.nodes.footnote import FootnoteNode
from mau.nodes.header import HeaderNode
from mau.nodes.node import Node, NodeContentMixin, NodeInfo, ValueNode
from mau.nodes.node_arguments import NodeArguments

MACRO_HELP = """
Syntax:

[NAME](ARGS)

A generic macro named NAME that contains the given ARGS.
"""

MACRO_CLASS_HELP = """
Syntax:

[class](class1, class2, ...)

A macro to assign classes to text.
"""

MACRO_LINK_HELP = """
Syntax:

[link](target[, text])

A macro that creates a link. The text of the link is the target itself
unless the option `text` is gien a value.
"""

MACRO_IMAGE_HELP = """
Syntax:

[image](uri[, alt_text, width, height])

A macro that inserts an image. The macro requires the `uri` and
accepts optional `alt_text`, `width`, and `height`.
"""

MACRO_HEADER_HELP = """
Syntax:

[header](header_alias)

A macro that inserts a link to a header. The macro requires
the header exernal ID as a parameter.
"""

MACRO_FOOTNOTE_HELP = """
Syntax:

[footnote](footnote_name)

A macro that inserts a link to a footnote. The macro requires
the footnote name associated with the relative data block.
"""


class MacroNode(Node):
    """This node contains a macro, with a name and arguments."""

    type = "macro"

    def __init__(
        self,
        name: str,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        self.name = name

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.name = self.name
        return new_node

    @property
    def custom_template_fields(self) -> dict:
        return {
            "name": self.name,
        }


class MacroClassNode(Node, NodeContentMixin):
    """Text with one or more classes."""

    type = "macro-class"

    def __init__(
        self,
        classes: Sequence[str],
        content: Sequence[Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)
        self.classes = classes
        NodeContentMixin.__init__(self, content)

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.classes = list(self.classes)

        # Recursive deep copies.
        self._deepcopy_content(new_node)

        return new_node


class MacroLinkNode(Node, NodeContentMixin):
    """This node contains a link."""

    type = "macro-link"

    def __init__(
        self,
        target: str,
        content: Sequence[Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        self.target = target
        NodeContentMixin.__init__(self, content)

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.target = self.target

        # Recursive deep copies.
        self._deepcopy_content(new_node)

        return new_node


class MacroImageNode(Node):
    """This node contains an inline image."""

    type = "macro-image"

    def __init__(
        self,
        uri: str,
        alt_text: str | None = None,
        width: str | None = None,
        height: str | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        self.uri = uri
        self.alt_text = alt_text
        self.width = width
        self.height = height

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.uri = self.uri
        new_node.alt_text = self.alt_text
        new_node.width = self.width
        new_node.height = self.height
        return new_node


class MacroHeaderNode(Node, NodeContentMixin):
    """This node contains a link to a header node."""

    type = "macro-header"

    def __init__(
        self,
        target_name: str,
        header: HeaderNode | None = None,
        content: Sequence[Node] | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        # This is the internal name of the
        # header that we are pointing to.
        self.target_name = target_name

        # The header linked by this macro.
        self.header = header

        NodeContentMixin.__init__(self, content)

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.target_name = self.target_name
        new_node.header = self.header

        # Recursive deep copies.
        self._deepcopy_content(new_node)

        return new_node


class MacroFootnoteNode(Node):
    """This node contains a link to a footnote node."""

    type = "macro-footnote"

    def __init__(
        self,
        name: str,
        footnote: FootnoteNode | None = None,
        parent: Node | None = None,
        arguments: NodeArguments | None = None,
        info: NodeInfo | None = None,
    ):
        super().__init__(parent=parent, arguments=arguments, info=info)

        self.name = name
        self.footnote = footnote

    def deepcopy(self, parent=None):  # pragma: no cover
        # Create a new node and perform base deepcopy.
        new_node = super().deepcopy(parent)

        # Shallow copies.
        new_node.name = self.name
        new_node.footnote = self.footnote
        return new_node


class MacroUnicodeNode(ValueNode):
    """This node contains a unicode code point."""

    type = "macro-unicode"


class MacroRawNode(ValueNode):
    """This node contains raw inline content."""

    type = "macro-raw"
