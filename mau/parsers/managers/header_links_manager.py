from __future__ import annotations

from mau.nodes.header import HeaderNode
from mau.nodes.macro import MacroHeaderNode
from mau.parsers.base_parser import create_parser_exception


class HeaderLinksManager:
    """This manager collects headers and link macros.
    When the manager process is run, all macros
    are updated and given the correct header as child.
    """

    def __init__(self):
        # This list contains the collected macros.
        self.macros: list[MacroHeaderNode] = []

        # This dictionary contains the headers,
        # the key is the header name.
        self.headers: dict[str, HeaderNode] = {}

    def add_header(self, header: HeaderNode):
        """Add a single header to the list
        of managed headers. Check that the header
        ID is not already in use."""
        if header.name in self.headers:
            raise create_parser_exception(
                f"Duplicate header id detected: {header.name}",
                context=header.info.context,
            )

        self.headers[header.name] = header

    def add_macros(self, macros: list[MacroHeaderNode]):
        """Add the given list of macros
        to the managed macros."""
        self.macros.extend(macros)

    def update(self, other: HeaderLinksManager):
        """Update the headers and macro nodes
        with those contained in another
        Header Links Manager."""
        self.add_macros(other.macros)

        for name, node in other.headers.items():
            self.add_header(node)

    def process(self):
        # Process each macro node, find the
        # header it mentions in the list of
        # headers, and connect the two.

        for macro in self.macros:
            try:
                macro.header = self.headers[macro.target_name]

                if not macro.content:
                    macro.content = [
                        node.deepcopy(parent=macro) for node in macro.header.content
                    ]
            except KeyError as exc:
                raise create_parser_exception(
                    f"Cannot find header with id {macro.target_name}",
                    context=macro.info.context,
                ) from exc
