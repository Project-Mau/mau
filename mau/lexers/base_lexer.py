import logging
import re
from typing import Callable

from mau.environment.environment import Environment
from mau.message import BaseMessageHandler, MauException, MauLexerErrorMessage
from mau.text_buffer import Context, Position, TextBuffer, adjust_context
from mau.token import Token, TokenType

logger = logging.getLogger(__name__)


def rematch(regexp, text):
    # Match the regexp on the current line.
    return re.match(regexp, text)


def create_lexer_exception(text: str, source: str, position: Position | None = None):
    message = MauLexerErrorMessage(text=text, source=source, position=position)

    return MauException(message)


def print_tokens(tokens: list[Token]):
    for token in tokens:
        print(f"{token.type} {repr(token.value)} {adjust_context(token.context)}")


class BaseLexer:
    """
    The base class for lexers.
    The lexer decomposes the input text into a list of tokens
    and provides basic navigation functions in the
    output results.

    This class provides the base machinery for a lexer,
    running a sequence of functions until one of them
    successfully identifies a token.
    """

    def __init__(
        self,
        text_buffer: TextBuffer,
        message_handler: BaseMessageHandler,
        environment: Environment | None = None,
    ):
        self.text_buffer: TextBuffer = text_buffer

        # This is the list of the tokens that
        # the lexer extracts.
        self.tokens: list[Token] = []

        # The last visited position. Used to detect loops.
        self._last_position: Position | None = None

        # The message handler instance.
        self.message_handler = message_handler

        # The configuration environment.
        self.environment: Environment = environment or Environment()

    @property
    def _current_char(self) -> str:
        # Return the current character.
        return self.text_buffer.current_char

    @property
    def _current_line(self) -> str:
        # Return the current line.
        return self.text_buffer.current_line

    @property
    def _position(self) -> Position:
        # Return the context.
        return self.text_buffer.position

    @property
    def _tail(self) -> str:
        # A wrapper to return the rest of the line.
        return self.text_buffer.tail

    def _nextline(self):
        # Skip the whole line including the EOL.
        self.text_buffer.nextline()

    def _skip(self, value):
        # Skip only the given amount of characters
        # This is very useful with regexp groups
        # that can be None.
        if value is not None:
            self.text_buffer.skip(len(value))

    def _create_token_and_skip(
        self, token_type, token_value: str | None = None
    ) -> Token:
        # Create the token and advance the position
        # in the text buffer to skip the characters
        # that are part of the token.

        # If the token value is None,
        # transform it into an empty string.
        # This is useful as regular expression
        # groups can be None if they are optional.
        token_value = token_value or ""

        # Get the initial position.
        initial_position = self._position

        # Move past the token_value.
        self.text_buffer.skip(len(token_value))

        # Get the final position.
        final_position = self._position

        # Create the context.
        context = Context(
            *initial_position,
            *final_position,
            self.text_buffer.source_filename,
        )

        token = Token(token_type, token_value, context)

        return token

    def process(self):
        """Process the text and extract tokens
        using the registered processing functions.
        """

        # Process tokens until we reach the end of file.
        self._process()
        while True:
            # Check if the last thing we processed is an EOF.
            # In that case the process is over.
            if len(self.tokens) > 0 and self.tokens[-1].type is TokenType.EOF:
                break

            # There are other tokens to find.
            self._process()

    def _process(self):
        # This is the core of the lexer.
        # It should not be overridden by child classes.
        #
        # The function tries each function in the list
        # returned by _process_functions and stores
        # all the resulting tokens.
        #
        # All lexers process first EOF, empty line, and
        # trailing spaces, then all the provided functions.
        # Last, the function calls the error function,
        # as it hasn't found a suitable processing function.
        #
        # The lexer actively monitors if the newly
        # processed token is different from the previous
        # one (context included).
        # If not, this means we entered an infinite loop,
        # and this might happen as the processing functions
        # are provided by subclasses, and they might
        # be incorrect, for example missing to skip
        # the content of the token.
        #
        # A lexer function must return None
        # when characters do not match its rule.

        process_functions = [
            self._process_eof,
            self._process_empty_line,
            self._process_trailing_spaces,
        ]
        process_functions.extend(self._process_functions())
        process_functions.append(self._process_error)

        # This detects infinite loops created by incomplete
        # lexing functions. Those functions keep trying
        # to parse the same context, so if we spot that
        # we are doing it we should raise an error.
        if self._last_position is not None and self._last_position == self._position:
            raise create_lexer_exception(
                text="Loop detected, cannot process context",
                source=self.text_buffer.source_filename,
                position=self._position,
            )  # pragma: no cover

        self._last_position = self._position

        for process_func in process_functions:
            # This ensures result is always either None or a list
            result = process_func()

            if result is None:
                continue

            self.tokens.extend(result)

            return

    def _process_functions(self) -> list[Callable[[], list[Token] | None]]:
        return [
            self._process_text,
        ]

    def _process_error(self):
        raise create_lexer_exception(
            text="Cannot process token.",
            source=self.text_buffer.source_filename,
            position=self._position,
        )

    def _process_eof(self) -> list[Token] | None:
        # If we are not at the end of
        # the buffer just return.
        if not self.text_buffer.eof:
            return None

        # Build the EOF token.
        tokens = [self._create_token_and_skip(TokenType.EOF)]

        return tokens

    def _process_empty_line(self) -> list[Token] | None:
        # This detects an fully empty line,
        # that we want to preserve.

        # Match a line of pure spaces.
        match = rematch(r"^\ *$", self._current_line)

        # If there is no match just return.
        if not match:
            return None

        # Build the EOL token, preserving spaces.
        tokens = [self._create_token_and_skip(TokenType.EOL, self._current_line)]

        # Move to the next line.
        self._nextline()

        return tokens

    def _process_trailing_spaces(self) -> list[Token] | None:
        # This detects and skips any trailing spaces,
        # reaches the end of line and proceeds to the next line.

        # Match only spaces from here
        # to the end of the line.
        match = rematch(r"\ *$", self._tail)

        # If there is no match just return.
        if not match:
            return None

        # Skip the spaces we found.
        self._skip(self._tail)

        # Move to the next line.
        self._nextline()

        return []

    def _process_text(self) -> list[Token] | None:
        # Build a text token with everything
        # contained in this line until the end.
        tokens = [
            self._create_token_and_skip(TokenType.TEXT, self._tail),
        ]

        # Move to the next line.
        self._nextline()

        return tokens
