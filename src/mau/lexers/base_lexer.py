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


class TokenError(ValueError):
    pass


class Token:
    def __init__(self, _type, value=None, position=None):
        self.type = _type
        self.value = str(value) if value is not None else None
        self.position = position

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


EOL = Token(TokenTypes.EOL)
EOF = Token(TokenTypes.EOF)
WS = partial(Token, TokenTypes.WHITESPACE)
Text = partial(Token, TokenTypes.TEXT)
Literal = partial(Token, TokenTypes.LITERAL)


class BaseLexer:
    def __init__(self, initial_position=None):
        self._text_buffer = text_buffer.TextBuffer()

        self._text_buffer.position
        self._buffer = []
        self._initial_position = initial_position or (0, 0)

        self.tokens = []

    @property
    def _token_position(self):
        return tuple(map(sum, zip(self._text_buffer.position, self._initial_position)))

    def process(self, text):
        self.tokens = []
        self.index = -1
        self._text_buffer.load(text)

        self._process()
        while self.tokens[-1].type is not TokenTypes.EOF:
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
            result = self._wrap(process_func())

            if result is None:
                continue

            self.tokens.extend(result)
            return

    def _wrap(self, result):
        # Makes sure the result is either None or a list of tokens
        if result is None:
            return

        if not isinstance(result, Sequence):
            return [result]

        return result

    def _nextline(self):
        # Carriage return =)
        self._initial_position = (self._initial_position[0], 0)

        # Skip the whole line including the EOL
        self._text_buffer.nextline()

    def _skip(self, steps=1):
        # Skip only the given amount of characters
        self._text_buffer.skip(steps)

    @property
    def _current_char(self):
        return self._text_buffer.current_char

    @property
    def _current_line(self):
        return self._text_buffer.current_line

    @property
    def _tail(self):
        return self._text_buffer.tail

    def _create_token(self, token_type, token_value=None):
        return Token(token_type, token_value, position=self._token_position)

    def _create_token_and_skip(self, token_type, token_value=None, skip_value=None):
        skip = next(x for x in [skip_value, token_value, ""] if x is not None)
        token = self._create_token(token_type, token_value)

        if token_type == TokenTypes.EOL:
            self._nextline()
        else:
            self._skip(len(skip))

        return token

    def _store(self, token_type, token_value=None, skip_value=None):
        self._buffer.append(
            self._create_token_and_skip(token_type, token_value, skip_value)
        )

    def _pop(self):
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
