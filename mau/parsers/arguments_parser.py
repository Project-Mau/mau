from __future__ import annotations

from collections.abc import Sequence

from mau.environment.environment import Environment
from mau.lexers.arguments_lexer import ArgumentsLexer
from mau.message import BaseMessageHandler
from mau.nodes.node import NodeInfo, ValueNode
from mau.nodes.node_arguments import NodeArguments, set_names
from mau.parsers.base_parser import BaseParser, create_parser_exception
from mau.parsers.preprocess_variables_parser import PreprocessVariablesParser
from mau.token import Token, TokenType

INTERNAL_TAG_PREFIX = "mau:"


class ArgumentsParser(BaseParser):
    lexer_class = ArgumentsLexer

    def __init__(
        self,
        tokens: list[Token],
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
        parent_node=None,
    ):
        super().__init__(tokens, message_handler, environment, parent_node)

        # Save the context of the first token
        # to make exceptions more useful.
        self.context = None
        if tokens:
            self.context = tokens[0].context

        # This flag is turned on as soon as
        # a named argument is parsed
        self._named_arguments_on = False

        # This is the list of unnamed argument nodes.
        self.unnamed_argument_nodes: list[ValueNode] = []

        # This is the list of named argument nodes.
        self.named_argument_nodes: dict[str, ValueNode] = {}

        # This is the list of tag nodes.
        self.tag_nodes: list[ValueNode] = []

        # This is the subtype node.
        self.subtype: ValueNode | None = None

        # This is the alias node.
        self.alias: ValueNode | None = None

    def _process_functions(self):
        return [
            self._process_named_argument,
            self._process_unnamed_argument,
        ]

    def _process_named_argument(self):
        # This parses a named argument in the form
        # key=value
        # or
        # key="value"

        # Get the token with the key.
        key_token = self.tm.get_token(TokenType.TEXT)

        # After a key there should be an equal.
        # If not, this function fails.
        self.tm.get_token(TokenType.LITERAL, "=")

        # Values can be surrounded by quotes.
        # If there are quotes we skip them.
        if self.tm.peek_token_is(TokenType.LITERAL, '"'):
            # Read and discard the opening quotes
            self.tm.get_token(TokenType.LITERAL, '"')

            # Get everything before the next double quotes.
            token = self.tm.collect_join([Token.generate(TokenType.LITERAL, '"')])

            # Read and discard the closing quotes
            self.tm.get_token(TokenType.LITERAL, '"')
        else:
            # Get everything before the comma or EOF.
            token = self.tm.collect_join([Token.generate(TokenType.LITERAL, ",")])

        # The comma is not there after the last argument,
        # so this is in a context manager as it might fail.
        with self.tm:
            self.tm.get_token(TokenType.LITERAL, ",")

        # Ignore whitespace after the comma.
        with self.tm:
            self.tm.get_token(TokenType.WHITESPACE)

        # Save the node.
        node = ValueNode(
            token.value.strip(),
            info=NodeInfo(context=token.context),
            parent=self.parent_node,
        )

        self.named_argument_nodes[key_token.value] = node

        # Mark the beginning of named arguments
        self._named_arguments_on = True

        return True

    def _process_unnamed_argument(self):
        # This parses an unnamed argument in the form
        # value
        # or
        # "value"

        # Unnamed arguments can't appear after named ones.
        if self._named_arguments_on:
            raise create_parser_exception(
                text="Unnamed arguments after named arguments are forbidden.",
                context=self.context,
            )

        # Values can be surrounded by quotes
        # If there are quotes we skip them.
        if self.tm.peek_token_is(TokenType.LITERAL, '"'):
            # Read and discard the opening quotes
            self.tm.get_token(TokenType.LITERAL, '"')

            # Get everything before the next double quotes.
            token = self.tm.collect_join([Token.generate(TokenType.LITERAL, '"')])

            # Read and discard the closing quotes
            self.tm.get_token(TokenType.LITERAL, '"')
        else:
            # Get everything before the comma or EOF.
            token = self.tm.collect_join([Token.generate(TokenType.LITERAL, ",")])

        # The comma is not there after the last argument,
        # so this is in a context manager as it might fail.
        with self.tm:
            self.tm.get_token(TokenType.LITERAL, ",")

        # Ignore whitespace after the comma.
        with self.tm:
            self.tm.get_token(TokenType.WHITESPACE)

        # Save the node.
        node = ValueNode(
            token.value,
            info=NodeInfo(context=token.context),
            parent=self.parent_node,
        )

        self.unnamed_argument_nodes.append(node)

        return True

    def _isolate_by_prefix(
        self, prefix: str, nodes: Sequence[ValueNode], unique=False
    ) -> Sequence[ValueNode]:
        # Isolate unnamed arguments
        # whose value starts with the
        # given prefix.

        # Find all nodes we are interested in.
        nodes = [i for i in nodes if i.value.startswith(prefix)]

        # Remove the prefix from their value.
        for i in nodes:
            i.value = i.value.removeprefix(prefix)

        # Check if We need to enforce the presence of a single node.
        if unique and len(nodes) > 1:
            raise create_parser_exception(
                text=f"Multiple nodes with prefix '{prefix}' detected.",
                context=self.context,
            )

        return nodes

    def _isolate_tags_and_subtype(self):
        # Isolate all tags.
        self.tag_nodes = self._isolate_by_prefix("#", self.unnamed_argument_nodes)

        # Isolate all subtypes.
        subtypes = self._isolate_by_prefix(
            "*", self.unnamed_argument_nodes, unique=True
        )

        # Isolate all aliases.
        aliases = self._isolate_by_prefix("@", self.unnamed_argument_nodes, unique=True)

        # Extract the subtype if present.
        self.subtype = next(iter(subtypes), None)

        # Extract the alias if present.
        self.alias = next(iter(aliases), None)

        # Remove tags and subtype from unnamed arguments.
        self.unnamed_argument_nodes = [
            i
            for i in self.unnamed_argument_nodes
            if i not in self.tag_nodes + subtypes + aliases
        ]

        if self.alias:
            # Get all aliases.
            replacements = self.environment.get(
                "mau.parser.aliases", Environment()
            ).asdict()

            # Get the current alias if present.
            replacement = replacements.get(self.alias.value)

            if replacement is None:
                raise create_parser_exception(
                    text=f"Alias '{self.alias.value}' cannot be found in 'mau.parser.aliases': {replacements}.",
                    context=self.context,
                )

            # Get the replacement named arguments.
            replacement_args = replacement.get("args", {})

            # Get the replacement names.
            replacement_names = replacement.get("names", [])

            # Get the replacement subtype.
            replacement_subtype = replacement.get("subtype", None)

            # We need to add those arguments as nodes
            # with the same context as the alias.
            # However, if the arguments are already there
            # we must not overwrite them.

            # These are the keys added by the alias
            # that are not already in the processed arguments.
            missing_keys = set(replacement_args.keys()) - set(
                self.named_argument_nodes.keys()
            )

            for key in missing_keys:
                context = self.alias.info.context
                value = replacement_args[key]

                self.named_argument_nodes[key] = ValueNode(
                    value,
                    info=NodeInfo(context=context),
                    parent=self.parent_node,
                )

            self.set_names(replacement_names)

            if not self.subtype and replacement_subtype:
                self.subtype = ValueNode(
                    replacement_subtype,
                    info=NodeInfo(context=self.alias.info.context),
                    parent=self.parent_node,
                )

    def set_names(self, positional_names: list[str]):
        self.unnamed_argument_nodes, self.named_argument_nodes = set_names(
            self.unnamed_argument_nodes, self.named_argument_nodes, positional_names
        )

    @property
    def arguments(self) -> NodeArguments:
        # Isolate internal tags.
        internal_tag_nodes = [
            node
            for node in self.tag_nodes
            if node.value.startswith(INTERNAL_TAG_PREFIX)
        ]
        internal_tags = [
            node.value.removeprefix(INTERNAL_TAG_PREFIX) for node in internal_tag_nodes
        ]

        tag_nodes = [node for node in self.tag_nodes if node not in internal_tag_nodes]
        tags = [node.value for node in tag_nodes]

        return NodeArguments(
            unnamed_args=[node.value for node in self.unnamed_argument_nodes],
            named_args={
                key: node.value for key, node in self.named_argument_nodes.items()
            },
            tags=tags,
            internal_tags=internal_tags,
            subtype=self.subtype.value if self.subtype else None,
        )

    def parse(self):
        """
        Process the extracted nodes and converts them into Python structures.
        Unnamed arguments become a list of values (similar to *args).
        Named arguments become a dictionary (similar to *kwargs).
        Tags are all the unnamed arguments whose value starts with `#`.
        Subtype is the unnamed argument whose value starts with `*`.
        There can't be more than one subtype.
        """

        super().parse()

        self._isolate_tags_and_subtype()


def process_arguments(
    arguments_token: Token,
    message_handler: BaseMessageHandler,
    environment: Environment | None = None,
) -> ArgumentsParser:
    # Unpack the text initial position.
    start_line, start_column = arguments_token.context.start_position

    # Get the text source.
    source_filename = arguments_token.context.source

    # Parse the arguments.
    arguments_parser = ArgumentsParser.lex_and_parse(
        text=arguments_token.value,
        message_handler=message_handler,
        environment=environment,
        start_line=start_line,
        start_column=start_column,
        source_filename=source_filename,
    )

    return arguments_parser


def process_arguments_with_variables(
    arguments_token: Token,
    message_handler: BaseMessageHandler,
    environment: Environment | None = None,
) -> ArgumentsParser:
    # Unpack the text initial position.
    start_line, start_column = arguments_token.context.start_position

    # Get the text source.
    source_filename = arguments_token.context.source

    # Replace variables in the text.
    preprocess_parser = PreprocessVariablesParser.lex_and_parse(
        text=arguments_token.value,
        message_handler=message_handler,
        environment=environment,
        start_line=start_line,
        start_column=start_column,
        source_filename=source_filename,
    )

    # The preprocess parser outputs a single node.
    text_token = preprocess_parser.get_processed_text()

    # Parse the arguments.
    arguments_parser = ArgumentsParser.lex_and_parse(
        text=text_token.value,
        message_handler=message_handler,
        environment=environment,
        start_line=start_line,
        start_column=start_column,
        source_filename=source_filename,
    )

    return arguments_parser
