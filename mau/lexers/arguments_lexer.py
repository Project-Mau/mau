from typing import Callable

from mau.lexers.base_lexer import BaseLexer, rematch
from mau.token import Token, TokenType


class ArgumentsLexer(BaseLexer):
    """This lexer processes a string of text
    (single line) that contains arguments.
    Arguments are separated by a comma and
    zero or more spaces, e.g.

    1,2,3, 4,  5,   6,7

    They can contain just a value as above
    or be a key and a value, e.g.

    1, b=42, c=123

    The arguments string can contain double
    quotes to include commas in a value, e.g.

    1, "2, 123", 3

    Double quotes can be escaped to be the
    literal character, e.g.

    "value1", "some \"value\""
    """

    def _process_functions(self) -> list[Callable[[], list[Token] | None]]:
        return [
            self._process_whitespace,
            self._process_literal,
            self._process_text,
        ]

    def _process_whitespace(self) -> list[Token] | None:
        # Find any amount of whitespace.
        match = rematch(r" +", self._tail)

        if not match:
            return None

        return [self._create_token_and_skip(TokenType.WHITESPACE, match.group())]

    def _process_literal(self) -> list[Token] | None:
        # Find if the current character is one
        # of the special characters we are
        # interested in, \=,"
        if self._current_char not in r'\=,"':
            return None

        return [self._create_token_and_skip(TokenType.LITERAL, self._current_char)]

    def _process_text(self) -> list[Token] | None:
        # Anything that is not a special character
        # or a space can become a text token.
        match = rematch(r'[^\\=," ]+', self._tail)

        if not match:  # pragma: no cover
            return None

        return [self._create_token_and_skip(TokenType.TEXT, match.group())]
