import re
import string
from functools import partial
from collections.abc import Sequence

from mau import text_buffer


class TokenTypes:
    EOL = "EOL"
    EOF = "EOF"
    LITERAL = "LITERAL"
    TEXT = "TEXT"
    WHITESPACE = "WHITESPACE"


class LexerError(ValueError):
    pass


class Token:
    """
    This represents a token.
    Tokens have a type, a value (the actual characters), and a position
    in the global text, expressed as a tuple of line and column
    """

    def __init__(self, _type, value=None, position=None):
        self.type = _type
        self.position = position

        # This ensures things like numbers or other
        # strange beasts are just treated as text.
        self.value = str(value) if value is not None else None

    def __str__(self):
        position_string = ""
        if self.position:
            position_string = f", line={self.position[0]}, col={self.position[1]}"

        value_string = ""
        if self.value is not None:
            value_string = f", '{self.value}'"

        return f"Token({self.type}{value_string}{position_string})"

    __repr__ = __str__

    def __eq__(self, other):
        if other.value is None:
            return self.type == other.type

        return (self.type, self.value) == (
            other.type,
            other.value,
        )

    def __hash__(self):
        return hash((self.type, self.value))

    def __len__(self):
        if self.value:
            return len(self.value)

        return 0

    def __bool__(self):
        return True


# These are convenient shortcuts
EOL = Token(TokenTypes.EOL)
EOF = Token(TokenTypes.EOF)
WS = partial(Token, TokenTypes.WHITESPACE)
Text = partial(Token, TokenTypes.TEXT)
Literal = partial(Token, TokenTypes.LITERAL)


class BaseLexer:
    """
    The base class for lexers.
    The lexer decomposes the input text into a list of tokens
    and provides basic navigation functions in the
    output results.
    """

    def __init__(self, initial_position=None):
        # Use a TextBuffer internally to manage the text
        self._text_buffer = text_buffer.TextBuffer()

        # A buffer of tokens, useful when you need to
        # collect them but later post-process them
        # before you actually store them as result.
        self._buffer = []

        self._initial_position = initial_position or (0, 0)

        # These are the tokens identified so far
        self.tokens = []

    @property
    def _token_position(self):
        # This returns the token position taking into
        # account that the initial position might
        # not be (0,0)
        return tuple(map(sum, zip(self._text_buffer.position, self._initial_position)))

    def context(self, token):
        """Returns the context of a token for error reporting purposes"""
        return self._text_buffer.context(*token.position)

    def process(self, text):
        # Reset the lexer
        self.tokens = []

        # Load the text into the TextBuffer
        self._text_buffer.load(text)

        # Process tokens until we reach the end of file
        self._process()
        while True:
            # Preprocess functions can return no tokens
            if len(self.tokens) > 0 and self.tokens[-1].type is TokenTypes.EOF:
                break

            self._process()

    def _process(self):
        # This should not be touched by child classes
        # as it is the core of the lexer. It tries
        # each function in the list returned by
        # _process_functions and stores all the resulting
        # tokens. A parsing function must return None
        # when characters do not match the rules.

        process_functions = self._process_functions()
        process_functions.append(self._process_error)

        for process_func in process_functions:
            # This ensures result is always either None or a list
            result = self._wrap(process_func())

            if result is None:
                continue

            self.tokens.extend(result)
            return

    def _wrap(self, result):
        # Makes sure the result is either None or a list of tokens
        # which makes  processing function that return a single token
        # more readable.

        if result is None:
            return

        if not isinstance(result, Sequence):
            return [result]

        return result

    def _nextline(self):
        # Carriage return =) go to column 0
        self._initial_position = (self._initial_position[0], 0)

        # Skip the whole line including the EOL
        self._text_buffer.nextline()

    def _skip(self, steps=1):
        # Skip only the given amount of characters
        self._text_buffer.skip(steps)

    @property
    def _current_char(self):
        # Return the current character
        return self._text_buffer.current_char

    @property
    def _current_line(self):
        # Return the current line
        return self._text_buffer.current_line

    @property
    def _tail(self):
        # A wrapper to return the rest of the line
        return self._text_buffer.tail

    def _create_token(self, token_type, token_value=None):
        # A wrapper to create a token with the current position.
        # This doesn't affect the position in the text being lexed
        return Token(token_type, token_value, position=self._token_position)

    def _create_token_and_skip(self, token_type, token_value=None, skip_value=None):
        # Create the token and skip the characters in the text

        # This skips the first non-None value between skip_value, token_type and the empty string
        skip = next(x for x in [skip_value, token_value, ""] if x is not None)

        # This creates the token
        token = self._create_token(token_type, token_value)

        # Perform the right skip
        if token_type == TokenTypes.EOL:
            self._nextline()
        else:
            self._skip(len(skip))

        return token

    def _store(self, token_type, token_value=None, skip_value=None):
        # Create and skip a token, then store it in the buffer
        self._buffer.append(
            self._create_token_and_skip(token_type, token_value, skip_value)
        )

    def _pop(self):
        # Get the content of the buffer
        tokens = list(self._buffer)
        self._buffer = []
        return tokens

    def _process_eof(self):
        try:
            self._current_line
        except text_buffer.EOFError:
            return self._create_token_and_skip(TokenTypes.EOF)

    def _process_eol(self):
        try:
            self._current_char
        except text_buffer.EOLError:
            return self._create_token_and_skip(TokenTypes.EOL)

    def _process_character(self):
        if self._current_char not in string.ascii_letters:
            return None

        self._store(TokenTypes.TEXT, self._current_char)
        return self._pop()

    def _process_whitespace(self):
        regexp = re.compile(r"\ +")

        match = regexp.match(self._tail)

        if not match:
            return None

        self._store(TokenTypes.WHITESPACE, match.group())
        return self._pop()

    def _process_functions(self):
        return [
            self._process_eof,
            self._process_eol,
            self._process_whitespace,
            self._process_character,
        ]

    def _process_error(self):
        raise LexerError(f'Can\'t process "{self._tail}"')

    def _insert(self, text):
        self._text_buffer.insert(text)

    def _rematch(self, regexp):
        # Compile the regexp and get a match on the current line
        regexp = re.compile(regexp)
        return regexp.match(self._current_line)
