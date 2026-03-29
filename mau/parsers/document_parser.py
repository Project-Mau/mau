# pylint: disable=too-many-lines

from __future__ import annotations

from dataclasses import dataclass, field
from functools import partial

from mau.environment.environment import Environment
from mau.lexers.document_lexer import DocumentLexer
from mau.message import BaseMessageHandler
from mau.nodes.document import DocumentNode
from mau.nodes.include import TocNode
from mau.nodes.node import Node, NodeInfo
from mau.parsers.base_parser import BaseParser
from mau.parsers.buffers.arguments_buffer import ArgumentsBuffer
from mau.parsers.buffers.control_buffer import ControlBuffer
from mau.parsers.buffers.label_buffer import LabelBuffer
from mau.parsers.document_processors.arguments import arguments_processor
from mau.parsers.document_processors.block import block_processor
from mau.parsers.document_processors.control import control_processor
from mau.parsers.document_processors.header import header_processor
from mau.parsers.document_processors.horizontal_rule import horizontal_rule_processor
from mau.parsers.document_processors.include import IncludeCall, include_processor
from mau.parsers.document_processors.label import label_processor
from mau.parsers.document_processors.list import list_processor
from mau.parsers.document_processors.paragraph import paragraph_processor
from mau.parsers.document_processors.variable_definition import (
    variable_definition_processor,
)
from mau.parsers.managers.blockgroup_manager import BlockGroupManager
from mau.parsers.managers.footnotes_manager import FootnotesManager
from mau.parsers.managers.header_links_manager import HeaderLinksManager
from mau.parsers.managers.toc_manager import TocManager
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.parsers.text_parser import TextParser
from mau.text_buffer import Context
from mau.token import Token, TokenType

DEFAULT_STYLE_ALIASES = {
    "+": "add",
    "-": "remove",
    "!": "important",
    "x": "error",
}

DEFAULT_ARGUMENT_ALIASES = {
    "source": {
        "args": {"engine": "source"},
        "names": ["language"],
    },
}


@dataclass
class DocumentParserOutput:
    document: Node | None = None
    toc: TocNode | None = None

    # The list of included calls.
    include_calls: list[IncludeCall] = field(default_factory=list)


# The DocumentParser is in charge of parsing
# the whole input, calling other parsers
# to manage single paragraphs or other
# things like variables.
class DocumentParser(BaseParser):
    lexer_class = DocumentLexer

    def __init__(
        self,
        tokens: list[Token],
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
        parent_node=None,
        forbidden_includes: list[str] | None = None,
    ):
        super().__init__(tokens, message_handler, environment, parent_node)

        # Define the default block aliases.
        base_environment = Environment.from_dict(
            {
                "source_highlight_style_aliases": DEFAULT_STYLE_ALIASES,
                "aliases": DEFAULT_ARGUMENT_ALIASES,
            },
            "mau.parser",
        )

        # Update the environment without
        # overwriting existing values.
        self.environment.update(base_environment, overwrite=False)

        # This is the function used to create internal IDs for headers.
        self.header_internal_id_function = self.environment.get(
            "mau.parser.header_internal_id_function", None
        )

        # This is the function used to create unique IDs for footnotes.
        self.footnote_unique_id_function = self.environment.get(
            "mau.parser.footnote_unique_id_function", None
        )

        self.header_links_manager: HeaderLinksManager = HeaderLinksManager()
        self.blockgroup_manager = BlockGroupManager()
        self.footnotes_manager = FootnotesManager(self.footnote_unique_id_function)
        self.toc_manager: TocManager = TocManager(self.header_internal_id_function)

        self.arguments_buffer: ArgumentsBuffer = ArgumentsBuffer()
        self.label_buffer: LabelBuffer = LabelBuffer()
        self.control_buffer: ControlBuffer = ControlBuffer()

        # The last index in the latest ordered list,
        # used to calculate the beginning value of them
        # next one when start=auto
        self.latest_ordered_list_index = 0

        # This is a list of files that cannot
        # be included by this file. This is a
        # simple mechanism to avoid infinite
        # recursive inclusion.
        # This is a list as we need to keep the
        # order of calls.
        self.forbidden_includes = forbidden_includes or []

        # This is the final output of the parser
        self.output = DocumentParserOutput()

        # Initialise the container node.
        document_node_class = self.environment.get(
            "mau.parser.document_wrapper", DocumentNode
        )

        self.parent_node = document_node_class()

    def _process_functions(self):
        # All the functions that this parser provides.

        return [
            self._process_eol,
            partial(horizontal_rule_processor, self),
            partial(variable_definition_processor, self),
            partial(label_processor, self),
            partial(control_processor, self),
            partial(arguments_processor, self),
            partial(header_processor, self),
            partial(block_processor, self),
            partial(include_processor, self),
            partial(list_processor, self),
            partial(paragraph_processor, self),
        ]

    def _parse_text(self, text: str, context: Context, parent: Node) -> list[Node]:
        # This parses a piece of text.
        # It runs the text through the preprocessor to
        # replace variables, then parses it storing
        # footnotes and internal links, and finally
        # returns the nodes.

        # Unpack the token initial position.
        start_line, start_column = context.start_position

        # Get the token source.
        source_filename = context.source

        # Replace variables
        preprocess_parser = PreprocessVariablesParser.lex_and_parse(
            text,
            self.message_handler,
            self.environment,
            start_line=start_line,
            start_column=start_column,
            source_filename=source_filename,
        )

        # If the preprocessor doesn't return any
        # node we can stop here.
        if not preprocess_parser.nodes:  # pragma: no cover
            return []

        # The preprocess parser outputs a single node.
        text = preprocess_parser.get_processed_text().value

        # Parse the text
        text_parser = TextParser.lex_and_parse(
            text,
            self.message_handler,
            self.environment,
            start_line=start_line,
            start_column=start_column,
            source_filename=source_filename,
        )

        # Extract the footnote mentions
        # found in this piece of text.
        self.footnotes_manager.add_footnote_macros(text_parser.footnote_macros)

        # Extract the header links found in this piece of text.
        self.header_links_manager.add_macros(text_parser.header_links)

        # Assign the given parent to each node.
        for i in text_parser.nodes:
            i.parent = parent

        return text_parser.nodes

    def pop_labels(self, node: Node):
        # Extract labels from the buffer and
        # store them in the given node.
        labels = self.label_buffer.pop()

        # Assign parenthood.
        # Each label node is a child of the
        # host node, and each text node inside
        # the label is a child of the label.
        for label_node in labels.values():
            label_node.parent = node

            for child in label_node.content:
                child.parent = label_node

        # Assign the labels to the node.
        node.labels = labels

    def _process_eol(self) -> bool:
        # This simply ignores the end of line.

        self.tm.get_token(TokenType.EOL)

        return True

    def finalise(self):
        super().finalise()

        # This processes all footnotes stored in
        # the manager merging mentions and data
        # and updating the nodes that contain
        # a list of footnotes.
        self.footnotes_manager.process()

        # Process ToC nodes.
        # This operation needs to be done before
        # we process header links, as it creates
        # the internal IDs for headers that are
        # used by the header links.
        self.toc_manager.process()

        # This processes all links stored in
        # the manager linking them to the
        # correct headers.
        self.header_links_manager.process()

        # Process block groups.
        self.blockgroup_manager.process()

        if not self.nodes:
            return self.output

        # Find the document context.
        context = Context.merge_contexts(
            self.nodes[0].info.context, self.nodes[-1].info.context
        )

        self.parent_node.content = self.nodes
        self.parent_node.info = NodeInfo(context=context)

        self.output.document = self.parent_node

        self.output.toc = TocNode(
            plain_entries=self.toc_manager.headers,
            nested_entries=self.toc_manager.nested_headers,
        )
