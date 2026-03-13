from mau.environment.environment import Environment
from mau.lexers.base_lexer import BaseLexer
from mau.message import BaseMessageHandler, MauException, MauParserErrorMessage
from mau.nodes.node import Node
from mau.text_buffer import Context, TextBuffer
from mau.token import Token, TokenType

from .managers.tokens_manager import TokensManager


def create_parser_exception(
    text: str,
    context: Context | None = None,
    help_text: str | None = None,
):
    message = MauParserErrorMessage(text=text, context=context, help_text=help_text)

    return MauException(message)


class BaseParser:
    text_buffer_class = TextBuffer
    lexer_class = BaseLexer

    def __init__(
        self,
        tokens: list[Token],
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
        parent_node=None,
    ):
        self.tm = TokensManager(tokens)

        # These are the nodes created by the parsing.
        self.nodes: list[Node] = []

        # The last processed token. Used to detect loops.
        self.last_processed_token: Token = Token(TokenType.EOF, "", Context.empty())

        # The message handler instance.
        self.message_handler = message_handler

        # The configuration environment
        self.environment: Environment = environment or Environment()

        # This is the parent node of all the nodes
        # created by this parser
        self.parent_node = parent_node

    def _save(self, node):
        # Store the node.
        node.set_parent(self.parent_node)

        self.nodes.append(node)

    def _process_functions(self):
        # The parse functions available in this parser
        return []

    def parse(self):
        """
        Run the parser on the lexed tokens.
        """

        # Loop on all lexed tokens until we reach EOF.

        while not self.tm.peek_token_is(TokenType.EOF):
            # This detects infinite loops created by incomplete
            # parsing functions. Those functions keep trying
            # to parse the same token, so if we spot that
            # we are doing it we should raise an error.
            next_token = self.tm.peek_token()

            if (
                next_token == self.last_processed_token
                and next_token.context == self.last_processed_token.context
            ):
                raise create_parser_exception(
                    f"Loop detected, cannot parse token: {next_token}.",
                    next_token.context,
                )  # pragma: no cover
            else:
                self.last_processed_token = next_token

            # Here we run all parsing functions provided by
            # the parser until one returns a sensible result.
            result = False
            for process_function in self._process_functions():
                # The context manager wraps the function so that
                # any exception leaves the parsed tokens as they
                # were at the beginning of the function execution.
                #
                # If the parse function is successful it returns
                # True. If the function raises an exception the
                # variable result is not set and the value is False.
                # Any other result returned by the function
                # is ignored.
                with self.tm:
                    result = process_function()

                if result is True:
                    # True means the function was successful
                    # and we can stop the loop.
                    break

            # If we get here and result is still False
            # we didn't find any function to parse the
            # current token.
            if result is False:
                raise create_parser_exception(
                    "Cannot parse token.",
                    self.tm.peek_token().context,
                )

        # Complete the parsing operations.
        self.finalise()

    @classmethod
    def lex_and_parse(
        cls,
        text: str,
        message_handler: BaseMessageHandler,
        environment: Environment | None,
        start_line: int = 0,
        start_column: int = 0,
        source_filename: str | None = None,
        **kwds,
    ):  # pragma: no cover
        # This classmethod lexes and parses the
        # given text using the current class as
        # parser and the associated classes (
        # class attributes) as text buffer and
        # lexer.

        # Initialise the text buffer.
        text_buffer = cls.text_buffer_class(
            text,
            start_line,
            start_column,
            source_filename,
        )

        # Initialise the lexer.
        lexer = cls.lexer_class(
            text_buffer,
            message_handler,
            environment,
        )

        # Lex the given text.
        lexer.process()

        # Initialise the parser.
        parser = cls(
            lexer.tokens,
            message_handler,
            environment,
            **kwds,
        )

        # Parse the tokens found by the lexer.
        parser.parse()

        return parser

    def finalise(self):  # pragma: no cover
        # This code is executed at the end of the
        # parsing stage. It provides a space for
        # one-off operations that have to be
        # done when the whole parsing is completed.
        pass
