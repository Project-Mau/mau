from mau.errors import MauError, MauErrorException
from mau.helpers import rematch
from mau.text_buffer.context import print_context
from mau.tokens.tokens import Token


class MauLexerError(MauError):
    source = "lexer"

    def print_details(self):  # pragma: no cover
        super().print_details()

        context = self.details["context"]
        print_context(context)


class TokenTypes:
    EMPTY = "EMPTY"
    EOF = "EOF"
    EOL = "EOL"
    LITERAL = "LITERAL"
    TEXT = "TEXT"
    WHITESPACE = "WHITESPACE"


class BaseLexer:
    """
    The base class for lexers.
    The lexer decomposes the input text into a list of tokens
    and provides basic navigation functions in the
    output results.
    """

    def __init__(self, environment):
        self.text_buffer = None

        # These are the tokens identified so far
        self.tokens = []

        # The last visited context. Used to detect loops.
        self.last_visited_context = None

        # The configuration environment
        self.environment = environment

    def process(self, text_buffer):
        self.text_buffer = text_buffer

        # Process tokens until we reach the end of file
        self._process()
        while True:
            # Check if the last thing we processed is an EOF
            if len(self.tokens) > 0 and self.tokens[-1].type is TokenTypes.EOF:
                break

            self._process()

        # if Token(TokenTypes.EOF) in self.tokens:
        #     self.tokens.remove(Token(TokenTypes.EOF))

    @property
    def _current_char(self):
        # Return the current character
        return self.text_buffer.current_char

    @property
    def _current_line(self):
        # Return the current line
        return self.text_buffer.current_line

    @property
    def _context(self):
        # Return the context
        return self.text_buffer.context

    @property
    def _tail(self):
        # A wrapper to return the rest of the line
        return self.text_buffer.tail

    def _nextline(self):
        # Skip the whole line including the EOL
        self.text_buffer.nextline()

    def _skip(self, value):
        # Skip only the given amount of characters
        # This is very useful with regexp groups
        # that can be None.
        if value is not None:
            self.text_buffer.skip(len(value))

    def _error(self, message=None):
        error = MauLexerError(
            message=message,
            details={
                "context": self._context,
            },
        )

        raise MauErrorException(error)

    def _process(self):
        # This should not be touched by child classes
        # as it is the core of the lexer. It tries
        # each function in the list returned by
        # _process_functions and stores all the resulting
        # tokens.
        # All lexers process first EOF and EOL, and last
        # an error. This is mandatory as the underlying
        # text buffer doesn't flinch when we are past
        # EOL or EOF, and returns an empty string.
        # However, this means the parse can't skip the
        # token (it's empty) and end up in an infinite
        # loop, so we have to actively check that.
        # A lexer function must return None
        # when characters do not match the rule.

        process_functions = [self._process_eof, self._process_eol]
        process_functions.extend(self._process_functions())
        process_functions.append(self._process_error)

        # This detects infinite loops created by incomplete
        # lexing functions. Those functions keep trying
        # to parse the same context, so if we spot that
        # we are doing it we should raise an error.
        if (
            self.last_visited_context is not None
            and self.last_visited_context == self._context
        ):
            self._error("Loop detected, cannot process context.")  # pragma: no cover

        self.last_visited_context = self._context

        for process_func in process_functions:
            # This ensures result is always either None or a list
            result = process_func()

            if result is None:
                continue

            self.tokens.extend(result)

            return

    def _process_functions(self):
        return [
            self._process_text_line,
        ]

    def _process_error(self):
        self._error("No function found to process context.")

    def _create_token(self, token_type, token_value=None):
        # Create a token at the current position,
        # passing the current context.
        # This doesn't change the position in the buffer

        return Token(token_type, token_value, self._context)

    def _create_token_and_skip(self, token_type, token_value):
        # Create the token and advance the position
        # in the text buffer to skip the characters
        # that are part of the token.

        token = self._create_token(token_type, token_value)

        self._skip(token_value)

        return token

    def _create_tokens_from_line(self, token_type):
        # Create a token of the given type using the
        # whole current line as value.
        # Returns the token and EOL, then moves
        # to the next line.

        tokens = [
            self._create_token_and_skip(token_type, self._current_line),
            self._create_token(TokenTypes.EOL),
        ]

        self._nextline()

        return tokens

    def _process_eof(self):
        if self.text_buffer.eof:
            return [self._create_token(TokenTypes.EOF)]

        return None

    def _process_eol(self):
        # This cannot use TextBuffer.eol as we want to eat any spaces
        # that are present in the line.
        match = rematch(r"\ *$", self._tail)

        if not match:
            return None

        token = self._create_token_and_skip(TokenTypes.EOL, self._tail)

        self._nextline()

        return [token]

    def _process_text_line(self):
        tokens = [
            self._create_token_and_skip(TokenTypes.TEXT, self._tail),
            self._create_token(TokenTypes.EOL),
        ]

        self._nextline()

        return tokens
